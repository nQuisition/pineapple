from peewee import Model, Database, SqliteDatabase
from typing import Dict, List, Type
from contextlib import contextmanager
import os


class InvalidModelException(Exception):
    pass


class DatabaseManager:
    db: Database = None
    models_by_plugin: Dict[str, List[Type[Model]]] = {}
    db_dir: str

    def __init__(self, db_dir):
        self.db = SqliteDatabase(None)
        self.db_dir = db_dir

    def register_plugin_models(self, plugin_name: str, models: List[Type[Model]]):
        if len(models) == 0:
            return
        for model in models:
            if not issubclass(model, Model):
                raise InvalidModelException
        self.models_by_plugin[plugin_name] = models.copy()

    # The reason it is a bit convoluted is because peewee doesn't really expect us to change databases once
    # initialized. The standard way would be to bind database in our model class:
    # class Model:
    #   class Meta:
    #     database = db
    # But since we need to change database for each server, I've decided to use context bind, even though docs
    # say that it is supposed to be used for testing. But hey, it works just fine here I think!
    @contextmanager
    def lock(self, guild_id: int, plugin_name: str):
        models = self.models_by_plugin[plugin_name]
        self.db.init(os.path.join(self.db_dir, str(guild_id) + '.sqlite'))
        try:
            self.db.connect()
            # Bind our models to the database and they will automatically unbind at the end of "with"
            with self.db.bind_ctx(models):
                self.db.create_tables(models)
                yield
        finally:
            self.db.close()
