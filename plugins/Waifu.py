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
        waifu_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
        waifu_request = requests.get("https://mywaifulist.moe/{}".format(path), headers=waifu_headers)
        if(waifu_request.status_code != 200):
            print("Non-200 response from mywaifulist.moe:\n{}".format(waifu_request.content))
            await self.waifu_error_message(message_object)
            return

        try:
            soup = bs(waifu_request.content, "html.parser")
            waifu_id = json.loads(soup.find("waifucore")["waifu-id"])
            waifu = self.call_waifu_api(waifu_id)
            embed = discord.Embed()
            embed.set_image(url=waifu["display_picture"])
        except KeyError:
            print("Non-200 response from mywaifulist.moe:\n{}".format(waifu_request.content))
            await self.waifu_error_message(message_object)
            return

        await self.pm.client.send_message(message_object.channel,
                                          "Your waifu is **{}** from **{}**".format(waifu["name"], waifu["series"]["name"]),
                                          embed = embed)

    def call_waifu_api(self, waifu_id):
        waifu_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        waifu_api_request = requests.get("https://mywaifulist.moe/api/waifu/{}".format(waifu_id), headers=waifu_headers)
        if(waifu_api_request.status_code != 200):
            print("Non-200 response from mywaifulist.moe:\n{}".format(waifu_api_request.content))
            return {}
        return json.loads(waifu_api_request.content)

    async def waifu_error_message(self, message_object):
        await self.pm.client.send_message(message_object.channel,
                                          "Error requesting Waifu")
