import random

import discord


class ClientWrapper(object):

    rng = random.Random()

    def __init__(self, pm):
        self.pluginManager = pm
        self.client = pm.client

    async def send_message(self, name, channel, message):
        em = discord.Embed(description=message, colour=self.get_color(name))
        msg = await channel.send(embed=em)
        return msg

    async def edit_message(self, name, old_message, new_message):
        em = discord.Embed(description=new_message, colour=self.get_color(name))
        await old_message.edit(embed=em)
        return old_message

    @staticmethod
    def get_color(name):
        ClientWrapper.rng.seed(name)
        r = ClientWrapper.rng.randint(0, 255)
        g = ClientWrapper.rng.randint(0, 255)
        b = ClientWrapper.rng.randint(0, 255)
        return discord.Color((r << 16) + (g << 8) + b)
