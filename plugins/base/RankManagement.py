from util import Events
from util.Ranks import Ranks
from AbstractPlugin import AbstractPlugin
from CoreModels import RankBinding


class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "RankManagement")

    @staticmethod
    def register_events():
        return [Events.Command("addadmin", desc="Add an admin group"),
                Events.Command("addmod", Ranks.Admin, desc="Add a mod group"),
                Events.Command("addmember", Ranks.Admin, desc="Add a member group")]

    def get_models(self):
        # TODO ideally we probably don't want to import other plugin's model and use it as our own. Reference instead?
        return [RankBinding]

    async def handle_command(self, message_object, command, args):
        if command == "addadmin":
            await self.admin(message_object, args[1])
        elif command == "addmod":
            await self.bind(message_object, args[1], "Mod")
        elif command == "addmember":
            await self.bind(message_object, args[1], "Member")

        self.pm.botPreferences.bind_roles(message_object.guild.id)

    async def admin(self, message_object, group):
        if message_object.author is message_object.guild.owner:
            with self.pm.dbManager.lock(message_object.guild.id, self.get_name()):
                RankBinding.insert(discord_group=group, rank="Admin").on_conflict_ignore().execute()

            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Group " + group + " was added as admin")

    async def bind(self, message_object, group, rank):
        if message_object.author is message_object.guild.owner:
            with self.pm.dbManager.lock(message_object.guild.id, self.get_name()):
                RankBinding.insert(discord_group=group, rank=rank).on_conflict_ignore().execute()

            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Group " + group + " was added as " + rank)
