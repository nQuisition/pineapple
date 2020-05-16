import random

import discord


class ClientWrapper(object):
    def __init__(self, pm):
        self.pluginManager = pm
        self.client = pm.client

    async def send_message(self, name, channel, message):
        em = discord.Embed(description=message, colour=self.get_color(name))
        msg = await channel.send(embed=em)
        return msg

    async def edit_message(self, name, old_message, new_message):
        em = discord.Embed(description=new_message, colour=self.get_color(name))
        msg = await self.client.edit_message(old_message, embed=em)
        return msg

    @staticmethod
    def get_color(name):
        random.seed(name)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return discord.Color((r << 16) + (g << 8) + b)
