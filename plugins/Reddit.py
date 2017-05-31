from util import Events
from util.Ranks import Ranks
import feedparser
import discord
import os
import sqlite3
import time
import traceback


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.last_post = dict()

    @staticmethod
    def register_events():
        """
        :return: A list of util.Events
        """
        return [Events.Loop("reddit_check"),
                Events.Command("reddit", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):
        """
        :param message_object: discord.Message object containing the message
        :param command: The name of the command (first word in the message, without prefix)
        :param args: List of words in the message
        """
        if command == "reddit":
            await self.enable_notification(message_object, args[1])

    async def handle_loop(self):
        for server in self.pm.client.servers:

            # Get subreddits to be checked
            # Connect to SQLite file for server in cache/SERVERID.sqlite
            if not os.path.exists("cache/"):
                os.mkdir("cache/")
            con = sqlite3.connect("cache/" + server.id + ".sqlite",
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            subreddits = list()
            try:
                with con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM reddit_notification")
                    rows = cur.fetchall()
                    for row in rows:
                        subreddits.append({"channel": row[0], "subreddit": row[1]})
            except sqlite3.OperationalError:
                continue

            # Check all active notification subscriptions for this server
            for subscription in subreddits:

                try:
                    d = feedparser.parse("https://www.reddit.com/r/" + subscription["subreddit"] +
                                         "/search?q=ups%3A10..9999999999&sort=new&restrict_sr=on&syntax=cloudsearch")

                    if subscription["channel"] not in self.last_post:
                        # No entries seen yet, set last post as last seen but don't post anything
                        self.last_post[subscription["channel"]] = {"id": d.entries[0].id,
                                                                   "date": time.mktime(d.entries[0].updated_parsed)}
                    elif self.last_post[subscription["channel"]]["id"] == d.entries[0].id:
                        # Entry is still the same, don't do anything
                        continue
                    elif self.last_post[subscription["channel"]]["id"] != d.entries[0].id:
                        # print(self.last_post[subscription["channel"]]["date"])
                        # print(time.mktime(d.entries[0].updated_parsed))
                        if self.last_post[subscription["channel"]]["date"] < time.mktime(d.entries[0].updated_parsed):
                            # New post found, update last post ID and notify server
                            self.last_post[subscription["channel"]] = {"id": d.entries[0].id,
                                                                       "date": time.mktime(d.entries[0].updated_parsed)}

                            await self.pm.client.send_message(discord.Object(id=int(subscription["channel"])),
                                                              "**New post on /r/" + subscription["subreddit"] +
                                                              " by " + d.entries[0].author + "**\n" + d.entries[0].link)
                        else:
                            self.last_post[subscription["channel"]] = {"id": d.entries[0].id,
                                                                       "date": time.mktime(d.entries[0].updated_parsed)}
                except:
                    # traceback.print_exc()
                    continue

    async def enable_notification(self, message_object, subreddit):
        # Connect to SQLite file for server in cache/SERVERID.sqlite
        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS reddit_notification(Channel TEXT PRIMARY KEY, Subreddit TEXT)")
            cur.execute(
                'INSERT OR REPLACE INTO reddit_notification(Channel, Subreddit) VALUES(?,?)',
                (message_object.channel.id, subreddit))
