from util import Events
from util.Ranks import Ranks
from AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "ModLogChannel")

    @staticmethod
    def register_events():
        return [Events.Command("setmodlogchannel", rank=Ranks.Mod,
                               desc="Set the channel to post mod log messages to.")]

    async def handle_command(self, message_object, command, args):
        if command == "setmodlogchannel":
            await self.set_modlog_channel(message_object)

    async def set_modlog_channel(self, message_object):
        self.pm.botPreferences.set_database_config_value(message_object.guild.id,
                                                         "modlog_channel",
                                                         message_object.channel.id)
        await message_object.channel.send("Set mod log channel to: #" + message_object.channel.name)
