from util import Events
from util.Ranks import Ranks
import requests
import os
import discord
import random


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.base_url = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=100&tags="
        self.base_src = "http://gelbooru.com/index.php?page=post&s=view&id="
        if not os.path.exists("cache/"):
            os.makedirs("cache")
        self.blk_file = open("cache/gelbooru_blacklist.txt", "a+")
        self.blacklist = set()
        for line in self.blk_file:
            self.blacklist.add(line.strip())  # defines a blacklist of terms

    @staticmethod
    def register_events():
        return [Events.Command("image",
                               desc="Search Gelbooru! Refer to the Gelbooru Cheat Sheet for tags "
                                    "http://gelbooru.com/index.php?page=help&topic=cheatsheet"),
                Events.Command("nsfw", desc="spicier search"),
                Events.Command("blacklist", Ranks.Mod,
                               desc="Adds gelbooru tag to blacklist")]

    async def handle_command(self, message_object, command, args):
        if command == "image":
            await self.search(message_object, args[1], nsfw=False)
        if command == "nsfw":
            await self.search(message_object, args[1], nsfw=True)
        if command == "remove":
            await self.remove(message_object, args[1])

    async def search(self, message_object, text, nsfw):
        text = text.lower()  # moves all tags to lowercase
        search_tags = set(text.split())  # splits tags on second_place
        if "rating:questionable" in search_tags:
            search_tags.discard("rating:questionable")  # no loopholes
        if not nsfw:
            search_tags.add("rating:safe")  # append safe tag to URL if not nsfw
        else:
            search_tags.add("rating:questionable")  # append safe tag to URL if not nsfw
        request_url = self.base_url
        for tag in search_tags.difference(self.blacklist):
            request_url += (tag + "%20")  # add tags not contained in blacklist to search
        for tag in self.blacklist:
            request_url += ("-" + tag + "%20")  # add "not tags" from blacklists to search
        response = requests.get(request_url)
        try:
            if len(response.json()) is 0:
                await self.pm.client.send_message(message_object.channel, "Can't find an image that matches your "
                                                                          "tag(s) :cry:")
                return
        except:
            await self.pm.client.send_message(message_object.channel, "Can't find an image that matches your "
                                                                      "tag(s) :cry:")
            return

        response = response.json()[random.randint(0, len(response.json()) - 1)]
        gel_url = self.base_src + str(response["id"])  # this is the link to the gelbooru page
        image_url = "http:" + response["file_url"]

        em = discord.Embed(colour=random.randint(0x0, 0xFFFFFF))
        em.set_image(url=image_url)
        await self.pm.client.send_message(message_object.channel, embed=em)
        await self.pm.client.send_message(message_object.channel, "**Source:** " + gel_url)

    async def remove(self, message_object, text):
        text = text.lower()  # moves all tags to lowercase
        block_tags = set(text.split())  # splits tags on second_place
        for item in block_tags.difference(self.blacklist):
            self.blk_file.write(item + "\n")
            self.blacklist.add(item)
        await self.pm.client.send_message(message_object.channel,
                                          "**Tags added**")
