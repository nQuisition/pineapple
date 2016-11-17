class Plugin(object):
	def __init__(self, pm):
		self.pm = pm
		
	def RegisterCommands(self):
		return ["help", "info", "halppl0x"]
		
	async def HandleCommand(self, messageObject, command, args):
		if command == "help":
			await self.help(messageObject)
			
	async def help(self, messageObject):
		tmp = await self.pm.client.send_message(messageObject.channel, 'Helphelp')