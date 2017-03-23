from util import Events
from util.Ranks import Ranks
import requests
import urllib.request
import os
import sqlite3
import random


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.base_url = "http://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=100&tags="
        self.base_src = "http://gelbooru.com/index.php?page=post&s=view&id="
        if not os.path.exists("cache/"):
            os.makedirs("cache")

    @staticmethod
    def register_events():
        return [Events.Command("image",
                               desc="Search Gelbooru! Refer to the Gelbooru Cheat Sheet for tags "
                                    "http://gelbooru.com/index.php?page=help&topic=cheatsheet"),
                Events.Command("nsfw", desc="spicier search"),
                Events.Command("blacklist", Ranks.Mod,
                               desc="Adds gelbooru tag to blacklist"),
                Events.Command("unblacklist", Ranks.Mod, desc="Remove a tag from the blacklist")]

    async def handle_command(self, message_object, command, args):
        if command == "image":
            await self.search(message_object, args[1], nsfw=False)
        if command == "nsfw":
            await self.search(message_object, args[1], nsfw=True)
        if command == "blacklist":
            if args[1] is None or args[1] == "":
                await self.print_blacklist(message_object)
            else:
                await self.add_blacklist(message_object, args[1])
        if command == "unblacklist":
            await self.remove_blacklist(message_object, args[1])

    async def search(self, message_object, text, nsfw):
        text = text.lower()  # moves all tags to lowercase
        search_tags = set(text.split())  # splits tags on second_place
        blacklist = self.get_blacklist(message_object)
        if len(search_tags) is 0:
            await self.pm.client.send_message(message_object.channel, "Please enter tags to search.:thinking:")
            return
        search_tags.discard("rating:questionable")  # no loopholes
        search_tags.discard("rating:safe")  # no loopholes
        search_tags.discard("rating:explicit")  # no loopholes

        if len(search_tags.intersection(blacklist)) > 0:  # if all tags filtered, exit
            await self.pm.client.send_message(message_object.channel,
                                              "The tags used have been blacklisted by an Admin. :cry:")
            return
        if not nsfw:
            search_tags.add("rating:safe")  # append safe tag to URL if not nsfw
        else:
            search_tags.add("-rating:safe")  # append safe tag to URL if not nsfw
        request_url = self.base_url
        for tag in search_tags.difference(blacklist):
            request_url += (tag + "%20")  # add tags not contained in blacklist to search
        for tag in blacklist:
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
        while len(response_tags.intersection(blacklist)) > 0:
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
                                                                      "upload. " + image_url)
        else:
            await self.pm.client.send_file(message_object.channel, filename)
            await self.pm.client.send_message(message_object.channel, "**Source:** <" + gel_url + ">")

        os.remove(filename)

    async def add_blacklist(self, message_object, text):
        """
        Add tags to the booru search blacklist
        :param message_object: Message containing the command
        :param text: Text to be split containing the tags
        :return: None
        """
        text = text.lower()  # moves all tags to lowercase
        block_tags = set(text.split())  # splits tags on second_place

        # Connect to SQLite file for server in cache/SERVERID.sqlite
        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        for item in block_tags:
            with con:
                cur = con.cursor()
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS booru_blacklist(Tag TEXT PRIMARY KEY)")
                cur.execute(
                    'INSERT OR IGNORE INTO booru_blacklist(Tag) VALUES(?)',
                    (item,))

        await self.pm.client.send_message(message_object.channel,
                                          "{} Tags added".format(len(block_tags)))

    async def remove_blacklist(self, message_object, text):
        """
        Remove tags from the booru search blacklist
        :param message_object: Message containing the command
        :param text: Text to be split containing the tags
        :return: None
        """
        text = text.lower()  # moves all tags to lowercase
        block_tags = set(text.split())  # splits tags on second_place

        # Connect to SQLite file for server in cache/SERVERID.sqlite
        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        for item in block_tags:
            with con:
                cur = con.cursor()
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS booru_blacklist(Tag TEXT PRIMARY KEY)")
                cur.execute(
                    'DELETE FROM booru_blacklist WHERE Tag = ?',
                    (item,))

        await self.pm.client.send_message(message_object.channel, "Tags removed from the blacklist")

    async def print_blacklist(self, message_object):
        """
        Remove tags from the booru search blacklist
        :param message_object: Message containing the command
        :param text: Text to be split containing the tags
        :return: None
        """
        tags = self.get_blacklist(message_object)
        msg = "Blacklisted tags: "
        for tag in tags:
            msg += tag + " "
        await self.pm.client.send_message(message_object.channel, msg)

    @staticmethod
    def get_blacklist(message_object):
        # Connect to SQLite file for server in cache/SERVERID.sqlite
        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        tags = list()
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM booru_blacklist")  # TODO: Improve loading to show more users
            rows = cur.fetchall()
            msg = "Blacklisted tags: "
            for row in rows:
                try:
                    tags.append(row[0])
                except:
                    continue
        return tags
