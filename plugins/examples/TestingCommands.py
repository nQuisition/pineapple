from util import Events
from util.Ranks import Ranks
from AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "TestingCommands")

    @staticmethod
    def register_events():
        return [Events.Command("role", Ranks.Member)]

    async def handle_command(self, message_object, command, args):
        if command == "role":
            await self.role(message_object, )

    async def role(self, message_object):
        await message_object.channel.send(str([role.name.replace("@", "(at)") for role in message_object.author.roles]))
