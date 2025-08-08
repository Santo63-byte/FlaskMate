# Copyright 2025-2026 by Santo Shaji. All Rights Reserved.
# FlaskMate is a web framework for building scalable and maintainable applications using Flask.
from typing import Literal, Type, Callable, Dict, Any, Optional, Union, TYPE_CHECKING
from flask import Flask, jsonify
from flaskmate.types import FlaskMateType, FlaskMateAppType as FlaskAppType
if(TYPE_CHECKING):
    from flaskmate.stdlib import CGAppController as FlaskMateApp,EntryNode, Annotations, CFM, GlobalContext

else:
    from flaskmate.controllers import CGAppController as FlaskMateApp 
    from flaskmate.modules.app.Nodes import EntryNode as EntryNode
    from flaskmate.modules.utils.annotations import Annotations
    from flaskmate.types import ConfigManagerAbstractType as CFM
    from flaskmate.modules.app.Lfc import GlobalContext
    
from flaskmate.modules.orchestration.exceptions.cgexception import CGException as FlaskmateException


"""FlaskMate is a web framework for building scalable and maintainable applications using Flask."""
__version__ = "0.1.x"
__name__ = "flaskmate"
__author__ = "CGFramework Team"
__description__ = "A framework for building scalable and maintainable applications using Flask."

jsonify: Callable[..., Any] = jsonify
DynastComponent = Annotations.DynastComponent
AutoLog=Annotations.AutoLog
ConfigManager = Annotations.ConfigManager
global_context = GlobalContext()

__all__ = [
    "FlaskMateApp",
    "FlaskMateType",
    "FlaskAppType",
    "EntryNode",
    "FlaskmateException",
    "Annotations",
    "jsonify",
    "AutoLog",
    "ConfigManager",
    "CFM",
    "global_context",
]

