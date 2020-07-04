from util import Events
from util.Ranks import Ranks
from AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "BotNick")

    @staticmethod
    def register_events():
        return [Events.Command("nick", Ranks.Admin,
                               desc="Change the nickname for the bot. Admin only")]

    async def handle_command(self, message_object, command, args):
        if command == "nick":
            await self.nick(message_object, args[1])

    async def nick(self, message_object, nick):
        await message_object.guild.me.edit(nick=nick)
