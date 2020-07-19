import re
import os
import json
import time
from typing import Dict
from asyncio import Lock
from aiohttp import ClientSession
from util import Events
from util.Ranks import Ranks
from AbstractPlugin import AbstractPlugin

default_currency_aliases = {
    '$': 'USD',
    'NT$': 'TWD',
    'RMB': 'CNY',
    '€': 'EUR',
    '£': 'GBP',
    '¥': 'JPY',
    'YEN': 'JPY',
    'DOLLAR': 'USD',
    'DOLLARS': 'USD',
    'EURO': 'EUR',
    'EUROS': 'EUR',
    'QUID': 'GBP'
}


class InvalidCacheException(Exception):
    pass


class JsonFileException(Exception):
    pass


class FixerApiException(Exception):
    def __init__(self, message):
        super().__init__('Fixer API error: ' + message)


class Plugin(AbstractPlugin):

    session: ClientSession
    lock: Lock
    api_key: str
    cache_path: str
    currency_aliases_path: str
    rates: Dict[str, float]
    currency_aliases: Dict[str, str]
    last_updated: int
    update_interval: int

    def __init__(self, pm):
        super().__init__(pm, "Currency")
        self.api_key = self.pm.botPreferences.get_config_value("Fixer", "apikey")
        self.cache_path = os.path.join(pm.cache_dir, 'currency.json')
        self.currency_aliases_path = os.path.join(pm.cache_dir, 'currency_aliases.json')
        self.update_interval = 60*60*6  # 6 hours
        self.session = ClientSession()
        self.lock = Lock()
        self.read_aliases_file()

    @staticmethod
    def register_events():
        return [Events.Message("Currency"),
                Events.Command("addcurrency", rank=Ranks.Mod, desc="Add currency alias"),
                Events.Command("removecurrency", rank=Ranks.Mod, desc="Remove currency alias"),
                Events.Command("listcurrencies", desc="List all known currency aliases")]

    # TODO move to utils or something?
    @staticmethod
    def read_json_file(path):
        if not os.path.exists(path):
            raise JsonFileException
        with open(path) as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                # invalid JSON
                raise JsonFileException

    async def handle_command(self, message_object, command, args):
        if command == 'addcurrency':
            upper = args[1].upper()
            parsed = re.match(r'^\s*([A-Z€£¥$ ]+)\s+([A-Z]+)\s*$', upper)
            if not parsed:
                await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                      'Incorrect argument supplied, the format is `addcurrency '
                                                      '<alias> <target>`')
                return
            alias = parsed.group(1)
            target = parsed.group(2)
            await self.add_currency_alias(message_object, alias, target)
        elif command == 'removecurrency':
            alias = args[1].upper()
            await self.remove_currency_alias(message_object, alias)
        elif command == 'listcurrencies':
            await self.list_currency_aliases(message_object)

    async def handle_message(self, message_object):
        upper = message_object.content.upper()
        parsed = re.match(r'^\s*([0-9]+(?:\.[0-9]*)?)\s*([A-Z€£¥$ ]+)\s+(?:TO|IN)\s+([A-Z€£¥$ ]+)\s*$', upper)
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
        try:
            cache_data = self.read_json_file(self.cache_path)
            self.last_updated = cache_data['_updated']
            self.rates = cache_data['rates']
            if not self.is_cache_valid():
                raise InvalidCacheException
        except JsonFileException:
            raise InvalidCacheException

    def read_aliases_file(self):
        try:
            self.currency_aliases = self.read_json_file(self.currency_aliases_path)
        except JsonFileException:
            self.currency_aliases = default_currency_aliases

    def save_currency_aliases(self):
        with open(self.currency_aliases_path, 'w') as json_file:
            json.dump(self.currency_aliases, json_file)

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
                    if not json_resp['success']:
                        raise FixerApiException(json_resp['error']['info'])
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
                if proper_from_currency not in self.currency_aliases:
                    return
                proper_from_currency = self.currency_aliases[proper_from_currency]
            if proper_to_currency not in self.rates:
                if proper_to_currency not in self.currency_aliases:
                    return
                proper_to_currency = self.currency_aliases[proper_to_currency]
            total = amount * self.rates[proper_to_currency] / self.rates[proper_from_currency]

            response_text = f'{amount} **{proper_from_currency}** = {total:.2f} **{proper_to_currency}**'
            await self.pm.clientWrap.send_message(self.name, message_object.channel, response_text)

        except Exception as e:
            print(e)
            # do nothing

    async def add_currency_alias(self, message_object, alias, target_currency):
        try:
            # populate local cache in case it is empty
            await self.update_cache()
            # I'm not sure if we should be checking this?
            if target_currency not in self.rates:
                await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                      f'Unknown currency **{target_currency}**')
                return
            # If alias was already defined it will overwrite it, OK I guess
            self.currency_aliases[alias] = target_currency
            self.save_currency_aliases()
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  f'**{alias}** is now an alias of **{target_currency}**')
        except Exception as e:
            print(e)
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  f'Error adding alias: {e}')

    async def remove_currency_alias(self, message_object, alias):
        if alias not in self.currency_aliases:
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  f'**{alias}** is not a known alias')
            return
        # If alias was already defined it will overwrite it, OK I guess
        del self.currency_aliases[alias]
        self.save_currency_aliases()
        await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                              f'Alias **{alias}** successfully deleted')

    async def list_currency_aliases(self, message_object):
        aliases_by_currency = {}
        for alias in self.currency_aliases:
            target = self.currency_aliases[alias]
            if target not in aliases_by_currency:
                aliases_by_currency[target] = []
            aliases_by_currency[target].append(alias)
        lines = []
        for currency, aliases in aliases_by_currency.items():
            aliases.sort()
            lines.append(f'{currency}: {", ".join(aliases)}')
        await self.pm.clientWrap.send_message(self.name, message_object.channel, '```' + '\n'.join(lines) + '```')
