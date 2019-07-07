from util import Events
from util.Ranks import Ranks
import discord


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Purge"

    @staticmethod
    def register_events():
        return [Events.Command("purge", Ranks.Mod, desc="Purge a number of messages. Mods and Admins only")]

    async def handle_command(self, message_object, command, args):
        if command == "purge":
            await self.purge(message_object, args[1])

    async def purge(self, message_object, num):
        await self.pm.client.purge_from(message_object.channel, limit=int(num))
        await self.pm.clientWrap.send_message(self.name, self.get_modlog_channel(message_object.server),
                                              message_object.author.display_name + " purged " + str(num)
                                              + " message(s) from #" + message_object.channel.name)

    def get_modlog_channel(self, server):
        channel = self.pm.botPreferences.get_database_config_value(server.id, "modlog_channel")
        if channel is not None:
            return discord.utils.find(lambda m: m.id == channel, server.channels)
