from util import Events
from util.Ranks import Ranks
import requests
import urllib.request
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
        if command == "blacklist":
            await self.remove(message_object, args[1])

    async def search(self, message_object, text, nsfw):
        text = text.lower()  # moves all tags to lowercase
        search_tags = set(text.split())  # splits tags on second_place
        if len(search_tags) is 0:
            await self.pm.client.send_message(message_object.channel, "Please enter tags to search.:thinking:")
            return
        search_tags.discard("rating:questionable")  # no loopholes
        search_tags.discard("rating:safe")  # no loopholes
        search_tags.discard("rating:explicit")  # no loopholes

        if len(search_tags.intersection(self.blacklist)) > 0:  # if all tags filtered, exit
            await self.pm.client.send_message(message_object.channel,
                                              "The tags used have been blacklisted by an Admin. :cry:")
            return
        if not nsfw:
            search_tags.add("rating:safe")  # append safe tag to URL if not nsfw
        else:
            search_tags.add("-rating:safe")  # append safe tag to URL if not nsfw
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

        img_response = response.json()[random.randint(0, len(response.json()) - 1)]
        retries = 5  # retry search 10 times
        response_tags = set(img_response["tags"].split())
        while len(response_tags.intersection(self.blacklist)) > 0:
            img_response = response.json()[random.randint(0, len(response.json()) - 1)]  # find new image from query
            response_tags = set(img_response["tags"].split())  # split tags from results
            retries -= 1  # decrement recount timer
            if retries is 0:
                await self.pm.client.send_message(message_object.channel, "Can't find an image that matches your "
                                                                          "tag(s) :cry:")
                return

        gel_url = self.base_src + str(img_response["id"])  # this is the link to the gelbooru page
        image_url = "http:" + img_response["file_url"]
        filename = "cache/temp" + image_url[-5:]
        # embeds are inconsistent, saves file instead.
        # em = discord.Embed(colour=random.randint(0x0, 0xFFFFFF))
        # em.set_image(url=image_url)
        # await self.pm.client.send_message(message_object.channel, embed=em)

        # downloads image to server
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(image_url, headers=hdr)
        page = urllib.request.urlopen(req)
        data = page.read()
        f = open(filename, 'wb+')
        f.write(data)
        f.close()

        if os.path.getsize(filename) > 8000000:
            await self.pm.client.send_message(message_object.channel, "The image that was found was too large to "
                                                                      "upload. Click here to view it: " + image_url)
        else:
            await self.pm.client.send_file(message_object.channel, filename)

        os.remove(filename)
        await self.pm.client.send_message(message_object.channel, "**Source:** " + gel_url)

    async def remove(self, message_object, text):
        text = text.lower()  # moves all tags to lowercase
        block_tags = set(text.split())  # splits tags on second_place
        for item in block_tags.difference(self.blacklist):
            self.blk_file.write(item + "\n")
            self.blacklist.add(item)
        await self.pm.client.send_message(message_object.channel,
                                          "**{} Tags added**".format(len(block_tags)))
