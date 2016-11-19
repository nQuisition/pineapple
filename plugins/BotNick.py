from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("nick")]

    async def handle_command(self, message_object, command, args):
        if command == "nick":
            await self.nick(message_object, args[1])

    async def nick(self, message_object, nick):
        await self.pm.client.change_nickname(message_object.server.me, nick)
