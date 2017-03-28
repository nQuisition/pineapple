import sqlite3
import os
from util import Events
from util.Ranks import Ranks


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "RankManagement"

    @staticmethod
    def register_events():
        return [Events.Command("addadmin", desc="Add an admin group"),
                Events.Command("addmod", Ranks.Admin, desc="Add a mod group"),
                Events.Command("addmember", Ranks.Admin, desc="Add a member group")]

    async def handle_command(self, message_object, command, args):
        if command == "addadmin":
            await self.admin(message_object, args[1])
        elif command == "addmod":
            await self.bind(message_object, args[1], "Mod")
        elif command == "addmember":
            await self.bind(message_object, args[1], "Member")

        self.pm.botPreferences.bind_roles(message_object.server.id)

    async def admin(self, message_object, group):
        if message_object.author is message_object.server.owner:
            if not os.path.exists("cache/"):
                os.makedirs("cache")

            # Connect to SQLite file for server in cache/SERVERID.sqlite
            con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

            with con:
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS rank_binding(DiscordGroup TEXT PRIMARY KEY, Rank TEXT)")
                cur.execute("INSERT OR IGNORE INTO rank_binding(DiscordGroup, Rank) VALUES(?, ?)", (group, "Admin"))

    async def bind(self, message_object, group, rank):
        if message_object.author is message_object.server.owner:
            if not os.path.exists("cache/"):
                os.makedirs("cache")

            # Connect to SQLite file for server in cache/SERVERID.sqlite
            con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

            with con:
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS rank_binding(DiscordGroup TEXT PRIMARY KEY, Rank TEXT)")
                cur.execute("INSERT OR IGNORE INTO rank_binding(DiscordGroup, Rank) VALUES(?, ?)", (group, rank))
                await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                      "Group " + group + " was added as " + rank)
