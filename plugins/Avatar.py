import discord

from util import Events
from AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "Avatar")

    @staticmethod
    def register_events():
        return [Events.Command("avatar", desc="Return the avatar of a user")]

    async def handle_command(self, message_object, command, args):
        if command == "avatar":
            await self.avatar(message_object)

    async def avatar(self, message_object):
        if len(message_object.mentions) == 1:
            await self.post_avatar(message_object, message_object.mentions[0])
        else:
            await self.post_avatar(message_object, message_object.author)

    async def post_avatar(self, message_object, user):
        if user.avatar_url is None or user.avatar_url == "":
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  user.display_name + " has no avatar set!")
            return

        em = discord.Embed(description="Avatar for " + user.display_name,
                           colour=self.pm.clientWrap.get_color(self.name))
        em.set_image(url=user.avatar_url)
        await message_object.channel.send(embed=em)
