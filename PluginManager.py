from os.path import dirname, basename
import glob
import importlib.util
import BotPreferences


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

    #
    def load_plugins(self):
        modules = glob.glob(dirname(__file__) + "/plugins/*.py")
        for f in modules:
            spec = importlib.util.spec_from_file_location(basename(f)[:-3], f)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            self.plugins[basename(f)] = plugin.Plugin(self)
        print(self.plugins)

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
        target = self.commands[command]
        await target.handle_command(message_object, command, args)

    async def handle_typing(self, channel, user, when):
        for name in self.typing:
            await self.typing[name].handle_typing(channel, user, when)

    async def handle_message_delete(self, message):
        for name in self.delete:
            await self.delete[name].handle_message_delete(message)

    ###
    #   Utility methods
    ###
    @staticmethod
    def bind_event(name, container, plugin, events):
        for cmd in (cmd for cmd in events if type(cmd).__name__ == name):
            container[cmd.name] = plugin
