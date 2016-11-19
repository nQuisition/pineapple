import datetime
from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("ping"), Events.Command("pong"), Events.Typing("test"), Events.MessageDelete("delete")]

    async def handle_command(self, message_object, command, args):
        if command == "ping":
            await self.ping(message_object, "Pong")
        elif command == "pong":
            await self.ping(message_object, "Ping")

    async def handle_typing(self, channel, user, when):
        await self.pm.client.send_message(channel, user.name + " is typing, wow!")

    async def handle_message_delete(self, message):
        await self.pm.client.send_message(message.channel,
                                          "Message deleted (" + message.author.name + "): " + message.content)

    async def ping(self, message_object, reply):
        speed = datetime.datetime.now() - message_object.timestamp
        await self.pm.client.send_message(message_object.channel,
                                          reply + " " + str(round(speed.microseconds / 1000)) + "ms")
