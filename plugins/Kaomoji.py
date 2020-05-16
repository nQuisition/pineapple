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
        await message_object.channel.send("( ͡° ͜ʖ ͡°)")

    async def wot(self, message_object):
        await message_object.channel.send("ಠ_ಠ")

    async def why(self, message_object):
        await message_object.channel.send("щ(ಠ益ಠщ)")
