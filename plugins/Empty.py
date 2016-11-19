from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return []

    async def handle_command(self, message_object, command, args):
        if command == "ping":
            await self.ping(message_object)

    async def nick(self, message_object):
        await self.pm.client.send_message(message_object.channel, 'Pong')
