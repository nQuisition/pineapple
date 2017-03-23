from configparser import ConfigParser, NoSectionError, NoOptionError
import os
import sqlite3
from util import Ranks


class BotPreferences(object):
    """
    The BotPreferences class manages access to the config.ini file. Plugins can access these settings,
    but new settings have to be added to the file manually.
    """

    # Prefix for commands, this can be changed to prevent issues with other bots in a server.
    # Multiple characters are supported
    commandPrefix = "!"

    # Bot nickname, the bot will use this nickname on startup. Can be temporarily changed with BotNick.py plugin
    nickName = "Pineapple"

    # Discord API OAuth token, used to login. Needs to be created by the bot owner.
    token = "DEFAULT_TOKEN"

    # Permissions list, each permission level will contain the names of groups that are assigned to it.
    # Ex: Admin: Admin, Owner / Member: Verified / Default: @everyone
    admin = list()
    mod = list()
    member = list()
    default = list()

    servers = dict()

    def __init__(self, pm):
        self.pluginManager = pm

        """
        Load the config file into memory and read their values
        """
        self.config = ConfigParser()
        self.reload_config()

    def bind_roles(self, server_id):
        """
        This method will read all the roles from the server database and add them to their container
        :param name: Permission level name in config file
        :param container: Container list to add the groups to
        """
        self.servers[server_id] = None

        if not os.path.exists("cache/"):
            os.makedirs("cache")

        # Connect to SQLite file for server in cache/SERVERID.sqlite
        con = sqlite3.connect("cache/" + server_id + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS rank_binding(DiscordGroup TEXT PRIMARY KEY, Rank TEXT)")
            cur.execute("SELECT * FROM rank_binding")
            rows = cur.fetchall()

            rc = Ranks.RankContainer()

            rc.default.append("@everyone")

            for row in rows:
                if row[1] == "Admin":
                    rc.admin.append(row[0])
                if row[1] == "Mod":
                    rc.mod.append(row[0])
                if row[1] == "Member":
                    rc.member.append(row[0])
            self.servers[server_id] = rc

    def reload_config(self):
        """
        Reload the values in the config file into memory
        """
        self.config.read("config.ini")

        # Discord login token
        self.token = self.get_config_value("client", "token")

        # Bot nickname
        self.nickName = self.get_config_value("client", "nick")

        # Command prefix
        self.commandPrefix = self.get_config_value("client", "prefix")

    def get_config_value(self, category, item):
        """
        Method that can be used by plugins to access values in the config file.
        :param category: Config category (ex: "Admin" is for [Admin])
        :param item: Config item in category
        :return: Value as a string
        """
        try:
            return str(self.config.get(category, item))
        except NoSectionError as e:
            print("Can't find section " + e.section)
        except NoOptionError as e:
            print("Can't find option " + e.option + ", " + e.section)
