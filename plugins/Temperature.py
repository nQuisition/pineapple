from util import Events
import re


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Temperature"
        self.match = re.compile(r"\-?\d*\.?\d+")

    @staticmethod
    def register_events():
        return [Events.Command("ftoc",
                               desc="Convert Fahrenheit to Celsius"),
                Events.Command("ctof",
                                desc="Convert Celsius to Fahrenheit")]

    async def handle_command(self, message_object, command, args):
        if args[1] is "":
            await self.pm.client.send_message(message_object.channel, "Please enter a temperature to convert")
        elif command == "ftoc":
            await self.ftoc(message_object, args[1])
        elif command == "ctof":
            await self.ctof(message_object, args[1])

    async def ftoc(self, message_object, ftemp):
        try:
            ftemp = float(self.match.search(ftemp).group(0))
            ctemp = (ftemp - 32) * (5/9)
            text = "{:.2f}°F is **{:.2f}°C**".format(ftemp, ctemp)
            await self.pm.clientWrap.send_message(self.name, message_object.channel, text)
        except:
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Please use a valid number to convert.")
    
    async def ctof(self, message_object, ctemp):
        try:
            ctemp = float(self.match.search(ctemp).group(0))
            ftemp = (ctemp * (9/5)) + 32
            text = "{:.2f}°C is **{:.2f}°F**".format(ctemp, ftemp)
            await self.pm.clientWrap.send_message(self.name, message_object.channel, text)
        except:
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Please use a valid number to convert.")
