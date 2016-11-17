class Plugin(object):
	def __init__(self, pm):
		self.pm = pm
		
	def RegisterCommands(self):
		return ["help", "info", "halppl0x"]
		
	async def HandleCommand(self, messageObject, command, args):
		if command == "help":
			await self.help(messageObject)
		if command == "info":
			await self.info(messageObject)
			
	async def help(self, messageObject):
		tmp = await self.pm.client.send_message(messageObject.channel, 'Helphelp')
	async def info(self, messageObject):
		tmp = await self.pm.client.send_message(messageObject.channel, 'Poke Dynista or Theraga for help')