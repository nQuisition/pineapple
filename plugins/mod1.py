class Plugin(object):
	def __init__(self, pm):
		self.pm = pm
		
	def RegisterCommands(self):
		return ["help", "info", "halppl0x"]
		
	async def HandleCommand(self, channel, command, args):
		if command == "help":
			await self.help(channel)
			
	async def help(self, channel):
		tmp = await self.pm.client.send_message(channel, 'Helphelp')