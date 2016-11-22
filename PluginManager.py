from os.path import dirname, basename
import glob
import importlib.util
import BotPreferences
from util.Ranks import Ranks


class PluginManager(object):
    # Container for all loaded plugins, dictionary: { filename: Plugin object }
    plugins = {}

    # Event handler containers, dictionary: { Event name: (plugin, minimum_rank) }
    commands = {}
    join = {}
    leave = {}
    typing = {}
    delete = {}

    # References to various managers
    botPreferences = None
    client = None

    def __init__(self, directory, client):
        """
        Initializes some fields for plugins to use
        :param directory: Plugin directory path, should always be "plugins/"
        :param client: discord.Client object
        """
        self.dir = directory
        self.botPreferences = BotPreferences.BotPreferences()
        self.client = client

    def load_plugins(self):
        """
        Load all plugin files in the folder (specified by self.directory) as modules
        and into a container dictionary list.
        :return:
        """
        # Find all python files in the plugin directory
        modules = glob.glob(dirname(__file__) + "/" + self.dir + "/*.py")

        # Iterate over each file, import them as a Python module and add them to the plugin list
        for f in modules:
            spec = importlib.util.spec_from_file_location(basename(f)[:-3], f)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            self.plugins[basename(f)] = plugin.Plugin(self)
            print("Loaded plugin: " + basename(f))

    def register_events(self):
        """
        Request every loaded plugin to present the events they would like to bind to. See util.Events for
        event descriptions
        """
        for name, plugin in self.plugins.items():
            events = plugin.register_events()

            self.bind_event("Command", self.commands, plugin, events)
            self.bind_event("UserJoin", self.join, plugin, events)
            self.bind_event("UserLeave", self.leave, plugin, events)
            self.bind_event("MessageDelete", self.delete, plugin, events)
            self.bind_event("Typing", self.typing, plugin, events)

    ###
    #   Handling events
    ###
    async def handle_command(self, message_object, command, args):
        try:
            target, rank = self.commands[command]
            if self.user_has_permission(message_object.author, rank):
                await target.handle_command(message_object, command, args)
            else:
                await self.client.send_message(message_object.channel,
                                               "You don't have the required permissions to do that (" + rank.name + ")")
        except KeyError:
            pass

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

    def user_has_permission(self, user, permission_level):
        """
        Checks whether one of the user's roles has the right level for the requested permission_level
        Roles are defined in config.ini and parsed in BotPreferences
        :param user: discord.Member object containing the user that triggered the event
        :param permission_level: Minimal permission level specified by the triggered event
        :return: True/False, whether used is allowed to trigger this event
        """
        highest_rank = Ranks.Default
        for rank in user.roles:
            if rank.name in self.botPreferences.admin and highest_rank < Ranks.Admin:
                highest_rank = Ranks.Admin
            elif rank.name in self.botPreferences.mod and highest_rank < Ranks.Mod:
                highest_rank = Ranks.Mod
            elif rank.name in self.botPreferences.member and highest_rank < Ranks.Member:
                highest_rank = Ranks.Member
        #print(highest_rank)
        return highest_rank >= permission_level
