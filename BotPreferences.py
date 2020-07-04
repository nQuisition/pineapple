from configparser import ConfigParser, NoSectionError, NoOptionError
from peewee import DoesNotExist

from util import Ranks
from CoreModels import RankBinding, ServerConfig


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

        with self.pluginManager.dbManager.lock(server_id, "Core"):
            rank_bindings = RankBinding.select()

        rc = Ranks.RankContainer()

        rc.default.append("@everyone")

        for rank_binding in rank_bindings:
            if rank_binding.rank == "Admin":
                rc.admin.append(rank_binding.discord_group)
            if rank_binding.rank == "Mod":
                rc.mod.append(rank_binding.discord_group)
            if rank_binding.rank == "Member":
                rc.member.append(rank_binding.discord_group)
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
        try:
            with self.pluginManager.dbManager.lock(server_id, "Core"):
                config_entry = ServerConfig.get_by_id(config_key)
        except DoesNotExist:
            return None
        return config_entry.value

    def set_database_config_value(self, server_id, config_key, config_value):
        """
        Method that can be used to set a server specific config value in the
        database.
        :param server_id: The server ID
        :param config_key: The config key
        :param config_value: The config value to set
        """
        with self.pluginManager.dbManager.lock(server_id, "Core"):
            ServerConfig.insert(key=str(config_key), value=str(config_value)).on_conflict_replace().execute()
