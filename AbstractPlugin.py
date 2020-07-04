from __future__ import annotations
from abc import ABC, abstractmethod
from peewee import Model
from typing import TYPE_CHECKING, List, Type
# avoid cyclic imports
if TYPE_CHECKING:
    from PluginManager import PluginManager


class AbstractPlugin(ABC):
    pm: PluginManager
    name: str

    def __init__(self, pm: PluginManager, name: str):
        self.pm = pm
        self.name = name

    def get_name(self):
        return self.name

    @staticmethod
    @abstractmethod
    def register_events():
        pass

    def get_models(self) -> List[Type[Model]]:
        return []
