from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("lenny"),Events.Command("wot"),Events.Command("why")]

    async def handle_command(self, message_object, command, args):
        if command == "lenny":
            await self.lenny(message_object)
        if command == "wot":
            await self.wot(message_object)
        if command == "why":
            await self.why(message_object)

    async def lenny(self, message_object):
        await self.pm.client.send_message(message_object.channel, "( ͡° ͜ʖ ͡°)")
        await self.pm.client.delete_message(message_object)

    async def wot(self, message_object):
        await self.pm.client.send_message(message_object.channel, "ಠ_ಠ")
        await self.pm.client.delete_message(message_object)

    async def why(self, message_object):
        await self.pm.client.send_message(message_object.channel, "щ(ಠ益ಠщ)")
        await self.pm.client.delete_message(message_object)

