#helper init
import importlib
from typing import Any
import json,logging,yaml
import uuid,click
from functools import lru_cache
import os

logger=logging.getLogger('app')

class CGHelper:
    def file_check(path: str) -> bool:
        """
        Check if a file or directory exists at the given path.
        """
        return os.path.exists(path)

    @lru_cache(maxsize=10)
    def loadJSon(path: str, mode: str ='r') -> Any:
        try:
            with open(path, mode) as openedfile:
                loaded_obj = json.load(openedfile)
            return loaded_obj
        except json.JSONDecodeError as jde:
            logger.error(f"Json File Error occurred:: {jde}")
            raise jde
        except FileNotFoundError as ffe:
            logger.error(f" Json File not found at {path} :: More info {ffe}")
            raise ffe
    
    @staticmethod
    def lazyload(mod_path: str, pointingclass: str):
        module = importlib.import_module(
            mod_path)  # dynamically loading module
        tobecalled = getattr(module, pointingclass)
        return tobecalled

    @staticmethod
    def generate_digit_id(length:int=12,appendcgname:bool=False):
        length= min(length,12)
        idb = str(uuid.uuid4())[:length]
        return f'cg_{idb}' if appendcgname else idb
    
    @staticmethod
    @lru_cache(maxsize=10)
    def loadYaml(path: str, mode: str ='r') -> Any:
        try:
            with open(path, mode) as openedfile:
                loaded_obj = yaml.safe_load(openedfile)
            return loaded_obj
        except yaml.YAMLError as yml:
            logger.error(f"Yaml File Error occurred :: {yml}")
            raise yml
        except FileNotFoundError as ffe:
            logger.error(f" Yaml File not found at {path} :: More info {ffe}")
            raise ffe
            
    @staticmethod
    def construct_modules(root: str, mainpath: str, servicefoldername: str) -> dict:
        
        """
        Constructs a dictionary of module paths based on the folder structure.
        """
        pycache= '__pycache__'
        mainfoldername = mainpath.split('\\')[0]
        def process_subfolders(folder_path, key_index):
            modules = {}
            for subfolder_name in os.listdir(folder_path):
                if subfolder_name != pycache:
                    subfolder_path = os.path.join(folder_path, subfolder_name)
                    if os.path.isdir(subfolder_path):
                        modules[f"m{key_index}"] = f"{servicefoldername}/{subfolder_name}"
                        key_index += 1
            return modules, key_index

        app_path = root.replace(mainpath, '')
        if not os.path.exists(app_path):
            raise FileNotFoundError(f"Application directory not found at {app_path}")

        modulesconfig = {"modules": {}}
        key_index = 1

        for folder_name in os.listdir(app_path):
            if folder_name == pycache:
                continue
            folder_path = os.path.join(app_path, folder_name)
            if os.path.isdir(folder_path):
                if folder_name == servicefoldername:
                    modules, key_index = process_subfolders(folder_path, key_index)
                    modulesconfig["modules"].update(modules)
                elif folder_name == mainfoldername:
                    modulesconfig["modules"][f"m{key_index}"] = folder_name
                    key_index += 1
        return modulesconfig
    
    @staticmethod
    def dot_to_path(dot_path:str) -> str:
        """
        Converts a dot-separated path to a file system path.
        """
        return dot_path.replace('.', '\\').replace('/', '\\')
