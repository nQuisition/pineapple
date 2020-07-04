from peewee import Model, TextField


class ServerConfig(Model):
    key = TextField(primary_key=True, column_name='Key')
    value = TextField(column_name='Value')

    class Meta:
        table_name = 'server_config'


class RankBinding(Model):
    discord_group = TextField(primary_key=True, column_name='DiscordGroup')
    rank = TextField(column_name='Rank')

    class Meta:
        table_name = 'rank_binding'
