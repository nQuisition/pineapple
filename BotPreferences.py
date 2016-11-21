from configparser import ConfigParser, NoSectionError, NoOptionError


class BotPreferences(object):
    commandPrefix = "!"
    nickName = "Pineapple"

    admin = list()
    mod = list()
    member = list()
    default = list()

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")

        # Discord login token
        self.token = self.get_config_value("client", "token")

        # Bot nickname
        self.nickName = self.get_config_value("client", "nick")

        # Command prefix
        self.commandPrefix = self.get_config_value("client", "prefix")

        # Bind roles
        self.bind_roles("Admin", self.admin)
        self.bind_roles("Mod", self.mod)
        self.bind_roles("Member", self.member)
        self.bind_roles("Default", self.default)

    def bind_roles(self, name, container):
        roles = self.get_config_value(name, "groups").split(",")
        for role in roles:
            container.append(role.strip())

    def reload_config(self):
        self.config.read("config.ini")

    def get_config_value(self, category, item):
        try:
            return str(self.config.get(category, item))
        except NoSectionError as e:
            print("Can't find section " + e.section)
        except NoOptionError as e:
            print("Can't find option " + e.option + ", " + e.section)
