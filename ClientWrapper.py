import random
import discord


class ClientWrapper(object):
    def __init__(self, pm):
        self.pluginManager = pm
        self.client = pm.client

    async def send_message(self, name, channel, message, embed=True):
        if embed:
            em = discord.Embed(description=message, colour=self.get_color(name))
            msg = await self.client.send_message(channel, embed=em)
            return msg
        normal = message
        msg = await self.client.send_message(channel, normal)
        return msg

    @staticmethod
    def get_color(name):
        random.seed(name)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return discord.Color((r << 16) + (g << 8) + b)
