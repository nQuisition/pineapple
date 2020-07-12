import re
import os
import json
import time
from typing import Dict
from asyncio import Lock
from aiohttp import ClientSession
from util import Events
from AbstractPlugin import AbstractPlugin

currency_aliases = {
    '$': 'USD',
    'NT$': 'TWD',
    'RMB': 'CNY',
    '€': 'EUR',
    '£': 'GBP',
    '¥': 'JPY'
}


class InvalidCacheException(Exception):
    pass


class Plugin(AbstractPlugin):

    session: ClientSession
    lock: Lock
    api_key: str
    cache_path: str
    rates: Dict[str, float]
    last_updated: int
    update_interval: int

    def __init__(self, pm):
        super().__init__(pm, "Currency")
        self.api_key = self.pm.botPreferences.get_config_value("Fixer", "apikey")
        self.cache_path = os.path.join(pm.cache_dir, 'currency.json')
        self.update_interval = 60*60*6  # 6 hours
        self.session = ClientSession()
        self.lock = Lock()

    @staticmethod
    def register_events():
        return [Events.Message("Currency")]

    async def handle_message(self, message_object):
        upper = message_object.content.upper()
        parsed = re.match(r'^\s*([0-9]+(?:\.[0-9]*)?)\s*([A-Z€£¥$]+)\s+(?:TO|IN)\s+([A-Z€£¥$]+)\s*$', upper)
        if not parsed:
            return
        amount = float(parsed.group(1))
        from_currency = parsed.group(2)
        to_currency = parsed.group(3)
        await self.convert(message_object, amount, from_currency, to_currency)

    def is_cache_valid(self):
        now = int(time.time())
        try:
            return self.last_updated + self.update_interval >= now
        except AttributeError:
            # self.last_updated not defined yet
            return False

    def read_cache_file(self):
        if not os.path.exists(self.cache_path):
            raise InvalidCacheException
        with open(self.cache_path) as json_file:
            try:
                cache_data = json.load(json_file)
                self.last_updated = cache_data['_updated']
                self.rates = cache_data['rates']
                if not self.is_cache_valid():
                    raise InvalidCacheException
            except json.JSONDecodeError:
                # invalid JSON, regenerate
                raise InvalidCacheException

    async def update_cache(self):
        if self.is_cache_valid():
            return
        async with self.lock:
            try:
                self.read_cache_file()
            except InvalidCacheException:
                now = int(time.time())
                request_url = f'http://data.fixer.io/api/latest?access_key={self.api_key}&format=1'
                async with self.session.get(request_url) as resp:
                    json_resp = await resp.json()
                    with open(self.cache_path, 'w') as json_file:
                        json_resp['_updated'] = now
                        json.dump(json_resp, json_file)
                    self.rates = json_resp['rates']
                    self.last_updated = now

    async def convert(self, message_object, amount, from_currency, to_currency):
        try:
            await self.update_cache()
            proper_from_currency = from_currency
            proper_to_currency = to_currency
            if proper_from_currency not in self.rates:
                if proper_from_currency not in currency_aliases:
                    return
                proper_from_currency = currency_aliases[proper_from_currency]
            if proper_to_currency not in self.rates:
                if proper_to_currency not in currency_aliases:
                    return
                proper_to_currency = currency_aliases[proper_to_currency]
            total = amount * self.rates[proper_to_currency] / self.rates[proper_from_currency]

            response_text = f'{amount} **{proper_from_currency}** = {total:.2f} **{proper_to_currency}**'
            await self.pm.clientWrap.send_message(self.name, message_object.channel, response_text)

        except Exception as e:
            print(e)
            # do nothing
