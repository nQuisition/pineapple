from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("help"), Events.Command("info"), Events.Command("hello")]

    async def handle_command(self, message_object, command, args):
        if command == "help":
            await self.help(message_object)
        if command == "info":
            await self.info(message_object)
        if command == "hello":
            await self.hello(message_object)

    async def help(self, message_object):
        await self.pm.client.send_message(message_object.channel, 'Help help')

    async def info(self, message_object):
        await self.pm.client.send_message(message_object.channel, 'Poke Dynista or Theraga for help')

    async def hello(self, message_object):
        msg = 'Hello {0.author.mention}'.format(message_object)
        await self.pm.client.send_message(message_object.channel, msg)
