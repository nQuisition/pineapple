from os.path import dirname, basename, isfile
import glob
import importlib.util
import BotPreferences

class PluginManager(object):
	plugins = {}
	commands = {}
	botPreferences = None
	client = None
	def __init__(self, dir, client):
		self.dir = dir
		self.botPreferences = BotPreferences.BotPreferences()
		self.client = client
	
	def LoadPlugins(self):
		modules = glob.glob(dirname(__file__)+"/plugins/*.py")
		for f in modules:
			spec = importlib.util.spec_from_file_location(basename(f)[:-3], f)
			plugin = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(plugin)
			self.plugins[basename(f)] = plugin.Plugin(self)
		print(self.plugins)
	
	def RegisterCommands(self):
		for name, plugin in self.plugins.items():
			cmds = plugin.RegisterCommands()
			for cmd in cmds:
				self.commands[cmd] = plugin

	async def HandleCommand(self, channel, command, args):
		target = self.commands[command]
		await target.HandleCommand(channel, command, args)