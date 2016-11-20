from configparser import ConfigParser


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
        self.token = str(self.config.get("client", "token"))

        # Bot nickname
        self.nickName = str(self.config.get("client", "nick"))

        # Command prefix
        self.commandPrefix = str(self.config.get("client", "prefix"))

        # Bind roles
        self.bind_roles("Admin", self.admin)
        self.bind_roles("Mod", self.mod)
        self.bind_roles("Member", self.member)
        self.bind_roles("Default", self.default)

    def bind_roles(self, name, container):
        roles = str(self.config.get(name, "groups")).split(",")
        for role in roles:
            container.append(role.strip())
