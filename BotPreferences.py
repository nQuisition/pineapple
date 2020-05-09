import os
import sqlite3
from configparser import ConfigParser, NoSectionError, NoOptionError

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
    nickName = "PineappleBot"

    # Discord API OAuth token, used to login. Needs to be created by the bot owner.
    token = ""

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
        """
        self.servers[server_id] = None

        if not os.path.exists("cache/"):
            os.makedirs("cache")

        # Connect to SQLite file for server in cache/SERVERID.sqlite
        con = sqlite3.connect("cache/" + str(server_id) + ".sqlite",
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
            print("Can't find section")
        except NoOptionError as e:
            print("Can't find option " + e.option + ", " + e.section)

    def get_database_config_value(self, server_id, config_key):
        """
        Method that can be used to get a server specific config value from the
        database.
        :param server_id: The server ID
        :param config_key: The config key
        :return: The found config value, None if no config entry was found.
        """
        # Connect to SQLite file for server in cache/SERVERID.sqlite
        con = sqlite3.connect("cache/" + str(server_id) + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        with con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS server_config(Key TEXT PRIMARY KEY UNIQUE, Value TEXT)")
            cur.execute("SELECT * FROM server_config WHERE Key = '" + config_key + "'")
            rows = cur.fetchall()
            if len(rows) == 1:
                return rows[0][1]
            else:
                return None

    def set_database_config_value(self, server_id, config_key, config_value):
        """
        Method that can be used to set a server specific config value in the
        database.
        :param server_id: The server ID
        :param config_key: The config key
        :param config_value: The config value to set
        """
        # Connect to SQLite file for server in cache/SERVERID.sqlite
        con = sqlite3.connect("cache/" + str(server_id) + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        with con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS server_config(Key TEXT PRIMARY KEY UNIQUE, Value TEXT)")
            query = "INSERT OR REPLACE INTO server_config(Key, Value) values('{0}', '{1}')".format(str(config_key),
                                                                                           str(config_value))
            cur.execute(query)
            con.commit()
