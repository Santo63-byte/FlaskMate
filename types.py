#define custom types here
from typing import Literal, Type, Callable, Dict, Any, Optional,Union
from flask import Flask
from abc import ABC, abstractmethod

class EntryNodeClass:
    """"""
FlaskMateType = Type[type]

FlaskMateAppType = Type[Any]  # Type for FlaskMate application instances


NodeType = Literal["entry_node", "dynast_node"]

class ConfigManagerAbstractType(ABC):
    
    """
    ConfigManagerType is an abstract base class for the ConfigManager.
    It defines the interface for the ConfigManager.
    """
    @abstractmethod
    def enrich(self, config:any) -> None:
        """Enrich the instance with the configuration."""
        pass