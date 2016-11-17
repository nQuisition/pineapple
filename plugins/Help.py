class Plugin(object):
	def __init__(self, pm):
		self.pm = pm
		
	def RegisterCommands(self):
		return ["help", "info", "hello"]
		
	async def HandleCommand(self, messageObject, command, args):
		if command == "help":
			await self.help(messageObject)
		if command == "info":
			await self.info(messageObject)
		if command == "hello":
			await self.hello(messageObject)
			
	async def help(self, messageObject):
		tmp = await self.pm.client.send_message(messageObject.channel, 'Helphelp')
	async def info(self, messageObject):
		tmp = await self.pm.client.send_message(messageObject.channel, 'Poke Dynista or Theraga for help')

	async def hello(self, messageObject):
			msg = 'Hello {0.author.mention}'.format(messageObject)
			await self.pm.client.send_message(messageObject.channel, msg)
