from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Help"

    @staticmethod
    def register_events():
        return [Events.Command("help", desc="Usage: help [module]|all, shows help text for a plugin, or a list of "
                                            "plugins if no plugin is specified."),
                Events.Command("hello"),
                Events.Command("info")]

    async def handle_command(self, message_object, command, args):
        if command == "help":
            if "all" in args[1]:
                await self.all_help(message_object)
            elif args[1] is not "":
                await self.show_help(message_object, args[1].lower())
            else:
                await self.show_help_assigned(message_object)
        if command == "info":
            await self.info(message_object)
        if command == "hello":
            await self.hello(message_object)

    async def all_help(self, message_object):
        hstr = "Complete Command List\n"
        for name, commands in self.pm.comlist.items():
            if len(commands) > 0:
                hstr += "\n**{0}**\n".format(name[:-3])
                for c, d in commands:
                    if d is not "":
                        hstr += "`" + self.pm.botPreferences.commandPrefix + c + "`: \n_" + d + "_\n"
                    else:
                        hstr += "`" + self.pm.botPreferences.commandPrefix + c + "`\n"

        # Split text into pieces of 1000 chars
        help_strings = list(map(''.join, zip(*[iter(hstr)] * 1000)))
        for string in help_strings:
            await self.pm.client.send_message(message_object.author, string)

        if not message_object.channel.is_private:
            await self.pm.client.delete_message(message_object)

    async def info(self, message_object):
        await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                              '**Pineapple**\nSource code available at: https://github.com/Dynista/pineapple')

    async def hello(self, message_object):
        msg = 'Hello {0.author.mention}'.format(message_object)
        await self.pm.clientWrap.send_message(self.name, message_object.channel, msg)

    async def show_help(self, message_object, args):
        try:
            hstr = "**{0}**:\n".format(args)
            for c, d in self.pm.comlist[args + ".py"]:
                hstr = hstr + "`" + self.pm.botPreferences.commandPrefix + c + "`: " + d + "\n"
            await self.pm.clientWrap.send_message(self.name, message_object.author, hstr)
        except KeyError:
            await self.pm.clientWrap.send_message(self.name, message_object.author,
                                                  ":exclamation: That\'s not a valid plugin name")
        if not message_object.channel.is_private:
            await self.pm.client.delete_message(message_object)

    async def show_help_assigned(self, message_object):
        x = "Bot Help\n```"
        for name, commands in self.pm.comlist.items():
            if len(commands) > 0:
                x = x + name[:-3] + " "

        x += "```\n`" + self.pm.botPreferences.commandPrefix + "help [help_topic]` to evoke a help topic.\n`" + \
             self.pm.botPreferences.commandPrefix + "help all` for all commands."
        await self.pm.clientWrap.send_message(self.name, message_object.author, x)
        if not message_object.channel.is_private:
            await self.pm.client.delete_message(message_object)
