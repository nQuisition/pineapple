from os.path import dirname, basename
import glob
import importlib.util
import BotPreferences
from util.Ranks import Ranks


class PluginManager(object):
    plugins = {}

    # Event handler containers
    commands = {}
    join = {}
    leave = {}
    typing = {}
    delete = {}

    botPreferences = None
    client = None

    def __init__(self, directory, client):
        self.dir = directory
        self.botPreferences = BotPreferences.BotPreferences()
        self.client = client

    # Load all plugin files in the /plugins folder as modules and into a container dictionary list
    def load_plugins(self):
        modules = glob.glob(dirname(__file__) + "/plugins/*.py")
        for f in modules:
            spec = importlib.util.spec_from_file_location(basename(f)[:-3], f)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            self.plugins[basename(f)] = plugin.Plugin(self)
        print(self.plugins)

    # Request every loaded plugin to present the events they would like to bind to
    def register_events(self):
        for name, plugin in self.plugins.items():
            events = plugin.register_events()

            # Refer to util.Events for appropriate names
            self.bind_event("Command", self.commands, plugin, events)
            self.bind_event("UserJoin", self.join, plugin, events)
            self.bind_event("UserLeave", self.leave, plugin, events)
            self.bind_event("MessageDelete", self.delete, plugin, events)
            self.bind_event("Typing", self.typing, plugin, events)

    ###
    #   Handling events
    ###
    async def handle_command(self, message_object, command, args):
        target, rank = self.commands[command]
        if self.user_has_permission(message_object.author, rank):
            await target.handle_command(message_object, command, args)
        else:
            await self.client.send_message(message_object.channel,
                                           "You do not have the required permissions to do that (" + rank.name + ")")

    async def handle_typing(self, channel, user, when):
        for obj in self.typing:
            name, rank = self.typing[obj]
            if self.user_has_permission(user, rank):
                await name.handle_typing(channel, user, when)

    async def handle_message_delete(self, message):
        for obj in self.delete:
            name, rank = self.delete[obj]
            if self.user_has_permission(message.author, rank):
                await name.handle_message_delete(message)

    ###
    #   Utility methods
    ###
    @staticmethod
    def bind_event(name, container, plugin, events):
        for cmd in (cmd for cmd in events if type(cmd).__name__ == name):
            # Data is stored as a tuple (Plugin, Required Rank) with the event binding's name as key in a dictionary
            container[cmd.name] = (plugin, cmd.minimum_rank)

    # Checks whether one of the user's roles has the right level for the requested permission_level
    # Roles are defined in config.ini and parsed in BotPreferences
    def user_has_permission(self, user, permission_level):
        highest_rank = Ranks.Default
        for rank in user.roles:
            if rank.name in self.botPreferences.admin and highest_rank < Ranks.Admin:
                highest_rank = Ranks.Admin
            elif rank.name in self.botPreferences.mod and highest_rank < Ranks.Mod:
                highest_rank = Ranks.Mod
            elif rank.name in self.botPreferences.member and highest_rank < Ranks.Member:
                highest_rank = Ranks.Member
        print(highest_rank)
        return highest_rank >= permission_level
