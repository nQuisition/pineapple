import glob
import os
import random

import discord

from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "PostImages"

    @staticmethod
    def register_events():
        return [Events.Command("pat", desc="Pat someone else"),
                Events.Command("lewd", desc="Use this if things get too lewd"),
                Events.Command("weeb", desc="When someone is being a weeb"),
                Events.Command("doushio", desc="Doushio"),
                Events.Command("rekt", desc="When someone just got rekt"),
                Events.Command("kiss", desc="Share a kiss"),
                Events.Command("boop", desc="boop~"),
                Events.Command("smug", desc="smug face"),
                Events.Command("fistbump", desc="Fist bump someone"),
                Events.Command("hug", desc="Hug someone"),
                Events.Command("dressage", desc="Dancing horses."),
                Events.Command("stopit", desc="Stop it."),
                Events.Command("smash", desc="Lemme smash."),
                Events.Command("dab", desc="Dab like a pro"),
                Events.Command("thanks", desc="Thank someone"),
                Events.Command("omg", desc="Oh my gosh. XD Lolz."),
                Events.Command("spice", desc="SMH Lens....")]

    async def handle_command(self, message_object, command, args):
        if command == "pat":
            await self.post_image_to_user(message_object, args[1], "pat",
                                          "you got a pat from **" + message_object.author.display_name + "**")
        if command == "kiss":
            await self.post_image_to_user(message_object, args[1], "kiss",
                                          "you got a kiss from **" + message_object.author.display_name + "**")
        if command == "fistbump":
            await self.post_image_to_user(message_object, args[1], "fistbump",
                                          "you got a fistbump from **" + message_object.author.display_name + "**")
        if command == "hug":
            await self.post_image_to_user(message_object, args[1], "hug",
                                          "you got a hug from **" + message_object.author.display_name + "**")
        if command == "lewd":
            await self.post_image(message_object, "lewd")
        if command == "weeb":
            await self.post_image(message_object, "weeb")
        if command == "doushio":
            await self.post_image(message_object, "doushio")
        if command == "rekt":
            await self.post_image(message_object, "rekt")
        if command == "boop":
            await self.post_image(message_object, "boop")
        if command == "smug":
            await self.post_image(message_object, "smug")
        if command == "dressage":
            await self.post_image(message_object, "dressage")
        if command == "stopit":
            await self.post_image(message_object, "stopit")
        if command == "smash":
            await self.post_image(message_object, "smash")
        if command == "dab":
            await self.post_image(message_object, "dab")
        if command == "thanks":
            await self.post_image(message_object, "thanks")
        if command == "omg":
            await self.post_image(message_object, "omg")
        if command == "spice":
            await self.post_image(message_object, "spice")

    async def post_image_to_user(self, message_object, user, type, message):
        files = glob.glob(os.getcwd() + "/images/" + type + "/" + '*.gif')
        files.extend(glob.glob(os.getcwd() + "/images/" + type + "/" + '*.png'))
        files.extend(glob.glob(os.getcwd() + "/images/" + type + "/" + '*.jpg'))
        file = random.choice(files)

        await message_object.delete()

        if user is None or user == "":
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Please specify a target to " + type + ".")
            return

        await message_object.channel.send(file=discord.File(file), content="**" + user + "** " + message)

    async def post_image(self, message_object, type):
        files = glob.glob(os.getcwd() + "/images/" + type + "/" + '*.gif')
        files.extend(glob.glob(os.getcwd() + "/images/" + type + "/" + '*.png'))
        files.extend(glob.glob(os.getcwd() + "/images/" + type + "/" + '*.jpg'))
        file = random.choice(files)
        await message_object.delete()
        await message_object.channel.send(file=discord.File(file), content=message_object.author.mention)
