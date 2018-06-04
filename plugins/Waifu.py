from bs4 import BeautifulSoup as bs
from random import random
from util import Events
import discord, json, requests


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Waifu"

    @staticmethod
    def register_events():
        return [Events.Command("waifu", desc="Return a random waifu from MyWaifuList.moe")]

    async def handle_command(self, message_object, command, args):
        if command == "waifu":
            await self.waifu(message_object)

    async def waifu(self, message_object):
        if random() <= 0.0039:
            await self.get_waifu(message_object, "waifu/hatsune-miku")
        else:
            await self.get_waifu(message_object, "random")

    async def get_waifu(self, message_object, path):
        waifu_request = requests.get("https://mywaifulist.moe/{}".format(path))
        if(waifu_request.status_code != 200):
            print("Non-200 response from mywaifulist.moe:\n{}".format(waifu_request.content))
            await self.waifu_error_message(message_object)
            return

        try:
            soup = bs(waifu_request.content, "html.parser")
            waifu = json.loads(soup.find("waifucore")["waifu-json"])
            embed = discord.Embed()
            embed.set_image(url=waifu["display_picture"])
        except KeyError:
            print("Non-200 response from mywaifulist.moe:\n{}".format(waifu_request.content))
            await self.waifu_error_message(message_object)
            return

        await self.pm.client.send_message(message_object.channel,
                                          "Your waifu is **{}** from **{}**".format(waifu["name"], waifu["series"]["name"]),
                                          embed = embed)

    async def waifu_error_message(self, message_object):
        await self.pm.client.send_message(message_object.channel,
                                          "Error requesting Waifu")
