from util import Events
from xml.etree import ElementTree
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

    async def handle_command(self, message_object, command, args):
        if command == "anime":
            await self.mal_search(message_object, args, "anime")
        if command == "manga":
            await self.mal_search(message_object, args, "manga")

    async def get_xml(self, category, name):
        """
        Queries the MAL search API to find a manga/anime based on a name
        :param category: String, "manga" or "anime"
        :param name: Search query
        :return: XML Data
        """
        auth = aiohttp.BasicAuth(login=self.username, password=self.password)
        url = 'https://myanimelist.net/api/' + category + '/search.xml'
        params = {'q': name}
        with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url, params=params) as response:
                data = await response.text()
                return data

    async def mal_search(self, message_object, args, category):
        """
        Process a MAL search command
        :param message_object: discord.Message object containing the message
        :param args: List of words in the command
        :param category: Type of search
        """
        data = await self.get_xml(category, ' '.join(args[1:]))
        if data == '':
            await self.pm.client.send_message(message_object.channel, "I didn't find anything :cry: ...")
            return

        root = ElementTree.fromstring(data)
        if len(root) == 0:
            await self.pm.client.send_message(message_object.channel, "Sorry, I found nothing :cry:.")
        elif len(root) == 1:
            entry = root[0]
        else:
            msg = "**Please choose one by giving its number.**\n"
            msg += "\n".join(['{} - {}'.format(n + 1, entry[1].text) for n, entry in enumerate(root) if n < 10])

            question = await self.pm.client.send_message(message_object.channel, msg)

            check = lambda m: m.content in map(str, range(1, len(root) + 1))
            resp = await self.pm.client.wait_for_message(
                author=message_object.author,
                check=check,
                timeout=20
            )
            if resp is None:
                return

            await self.pm.client.delete_message(question)
            await self.pm.client.delete_message(resp)

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
                msg += "**{}** {}\n".format(k.capitalize() + ":", html.unescape(spec.text.replace('<br />', '')))
        msg += "http://myanimelist.net/{}/{}".format(category, entry.find('id').text)

        await self.pm.client.send_message(message_object.channel, msg)
