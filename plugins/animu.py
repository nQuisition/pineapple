from configparser import ConfigParser
import asyncio
from util import Events
from xml.etree import ElementTree
import re
import aiohttp
import html


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.username = self.pm.botPreferences.get_config_value("MAL", "username")
        self.password = self.pm.botPreferences.get_config_value("MAL", "password")

    @staticmethod
    def register_events():
        return [Events.Command("anime"), Events.Command("manga")]

    async def get_xml_anime(self, name):
        auth = aiohttp.BasicAuth(login=self.username, password=self.password)
        url = 'https://myanimelist.net/api/anime/search.xml'
        params = {
            'q': name
        }
        with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url, params=params) as response:
                print(response)
                data = await response.text()
                return data

    async def get_xml_manga(self, name):
        auth = aiohttp.BasicAuth(login=self.username, password=self.password)
        url = 'https://myanimelist.net/api/manga/search.xml'
        params = {
            'q': name
        }
        with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url, params=params) as response:
                print(response)
                data = await response.text()
                return data

    async def handle_command(self, message_object, command, args):
        if command == "anime":
            await self.anime(message_object)
        if command == "manga":
            await self.manga(message_object)

    async def anime(self, message_object):
        rule = r'!(anime) (.*)'
        check = re.match(rule, message_object.content)
        nature, name = check.groups()

        data = await self.get_xml_anime(name)
        if data == '':
            await self.pm.send_message(
                message_object.channel,
                'I didn\'t find anything :cry: ...'
            )
            return

        root = ElementTree.fromstring(data)
        if len(root) == 0:
            await self.pm.send_message(
                message_object.channel,
                'Sorry, I found nothing :cry:.'
            )
        elif len(root) == 1:
            entry = root[0]
        else:
            msg = "**Please choose one by giving its number.**\n"
            msg += "\n".join(['{} - {}'.format(n + 1, entry[1].text) for n, entry in enumerate(root) if n < 10])

            await self.pm.client.send_message(message_object.channel, msg)

            check = lambda m: m.content in map(str, range(1, len(root) + 1))
            resp = await self.pm.client.wait_for_message(
                author=message_object.author,
                check=check,
                timeout=20
            )
            if resp is None:
                return

            entry = root[int(resp.content) - 1]

        switcher = [
            'english',
            'score',
            'type',
            'episodes',
            'volumes',
            'chapters',
            'status',
            'start_date',
            'end_date',
            'synopsis'
        ]

        msg = '\n**{}**\n\n'.format(entry.find('title').text)
        for k in switcher:
            spec = entry.find(k)
            if spec is not None and spec.text is not None:
                msg += '**{}** {}\n'.format(k.capitalize() + ':', html.unescape(spec.text.replace('<br />', '')))
        msg += 'http://myanimelist.net/{}/{}'.format(nature, entry.find('id').text)

        await self.pm.client.send_message(
            message_object.channel,
            msg
        )

    async def manga(self, message_object):

        rule = r'!(manga) (.*)'
        check = re.match(rule, message_object.content)
        nature, name = check.groups()

        data = await self.get_xml_manga(name)
        if data == '':
            await self.pm.send_message(
                message_object.channel,
                'I didn\'t find anything :cry: ...'
            )
            return

        root = ElementTree.fromstring(data)
        if len(root) == 0:
            await self.pm.send_message(
                message_object.channel,
                'Sorry, I found nothing :cry:.'
            )
        elif len(root) == 1:
            entry = root[0]
        else:
            msg = "**Please choose one by giving its number.**\n"
            msg += "\n".join(['{} - {}'.format(n + 1, entry[1].text) for n, entry in enumerate(root) if n < 10])

            await self.pm.client.send_message(message_object.channel, msg)

            check = lambda m: m.content in map(str, range(1, len(root) + 1))
            resp = await self.pm.client.wait_for_message(
                author=message_object.author,
                check=check,
                timeout=20
            )
            if resp is None:
                return

            entry = root[int(resp.content) - 1]

        switcher = [
            'english',
            'score',
            'type',
            'episodes',
            'volumes',
            'chapters',
            'status',
            'start_date',
            'end_date',
            'synopsis'
        ]

        msg = '\n**{}**\n\n'.format(entry.find('title').text)
        for k in switcher:
            spec = entry.find(k)
            if spec is not None and spec.text is not None:
                msg += '**{}** {}\n'.format(k.capitalize() + ':', html.unescape(spec.text.replace('<br />', '')))
        msg += 'http://myanimelist.net/{}/{}'.format(nature, entry.find('id').text)

        await self.pm.client.send_message(
            message_object.channel,
            msg
        )
