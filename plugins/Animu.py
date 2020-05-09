import discord
import requests

from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Animu"
        self.username = self.pm.botPreferences.get_config_value("MAL", "username")
        self.password = self.pm.botPreferences.get_config_value("MAL", "password")

    @staticmethod
    def register_events():
        return [Events.Command("anime",desc="Search MAL for an anime"), Events.Command("manga",desc="Search MAL for a manga")]

    async def handle_command(self, message_object, command, args):
        if command == "anime":
            await self.mal_search(message_object, args, "anime")
        if command == "manga":
            await self.mal_search(message_object, args, "manga")

    async def get_json(self, category, name):
        """
        Queries the MAL search API to find a manga/anime based on a name
        :param category: String, "manga" or "anime"
        :param name: Search query
        :return: XML Data
        """
        url = 'https://api.jikan.moe/v3/search/' + category + '?q=' + name
        return requests.get(url).json()

    async def mal_search(self, message_object, args, category):
        """
        Process a MAL search command
        :param message_object: discord.Message object containing the message
        :param args: List of words in the command
        :param category: Type of search
        """
        data = await self.get_json(category, ' '.join(args[1:]))
        if 'error' in data:
            await message_object.channel.send("Error occurred while searching.")
            return

        root = data['results']
        if len(root) == 0:
            await message_object.channel.send("No results.")
        elif len(root) == 1:
            entry = root[0]
        else:
            msg = "**Please choose one by giving its number.**\n"
            msg += "\n".join(['{} - {}'.format(n + 1, entry['title']) for n, entry in enumerate(root) if n < 10])

            question = await message_object.channel.send(msg)

            def check(m):
                return m.author == message_object.author and m.content in map(str, range(1, len(root) + 1))

            resp = await self.pm.client.wait_for('message', check=check, timeout=20)
            if resp is None:
                return

            await question.delete()
            await resp.delete()

            entry = root[int(resp.content) - 1]

        switcher = [
            'score',
            'type',
            'episodes',
            'volumes',
            'chapters',
            'start_date',
            'end_date',
            'synopsis'
        ]

        msg = '\n**{}**\n\n'.format(entry['title'])
        for k in switcher:
            if k in entry and entry[k] is not None:
                msg += "**{}**: {}\n".format(k.capitalize(), entry[k])
        msg += entry['url']

        em = discord.Embed(description=msg, colour=self.pm.clientWrap.get_color(self.name))
        em.set_image(url=entry['image_url'])
        await message_object.channel.send(embed=em)
