from flaskmate.modules.utils.classes import SLTC
import threading
import typing as t
from flask import Flask


class DependantConstants(SLTC):
    """
    This class contains the constants used for the application starting. The constants are related to dependant application instance.
    
    The class is designed to be singleton and thread-safe, hence it acts a transactional instance to recieve the dependant application information
    It contains the following properties:
    
    * the root object of the dependant
    * dependant application's config metadata 
    * the name of the dependant application
    * the version of the dependant application
    * the nodes of the dependant application (Dynast and Entry nodes)
    * the annotations instances of the dependant application
    * the constants of the dependant application( file names, etc.)
    """
    def __init__(self):
        self._flaskapp: t.Optional[t.Type[Flask]] = None
        self._dependantnodes: dict= {}
        self._configmetadata :dict[dict]= {
            "application": None,
            "services": None,
            "logs": None,
            "dynastnodes": None,
            "security": None,
            "database": None,
            "resources": None
        }
        self._tdlock = threading.RLock()  # Using RLock to allow nested locking
        self._root_path:str = ""
        self._appname:str = ""  
        self._version:str = "" 
        self._txnCode:str = "<cg_empty_txn>"
        self._txnMethod:str = "unknown"
        self._clientaddress:any = "unknown"
        self._logsconfig:dict = {}
        self._externalcfg:any = None
        self._applicationLogs:any = None  
        self._registeredDynastComponents: list = []
        self._resources: object = None 
        self._cfgmanager: dict = {}
        self._mpath: str = ""
        self._svspath: str = ""
        self._servicesabspath: str = ""
        self._applicationparentpath: str = ""

    # Constants (do not need thread safety)
    yml:list = ['yaml', 'yml']
    json: str = "json"
    app_yml: str = "app_config.yml"
    modules_file: str = "modules.json"
    mpathdefault:str = "main/src"
    svspathdefault:str = "services"
    # Thread-safe properties
    @property
    def root_path(self):
        with self._tdlock:
            return self._root_path

    @root_path.setter
    def root_path(self, value):
        with self._tdlock:
            self._root_path = value

    @property
    def appname(self):
        with self._tdlock:
            return self._appname

    @appname.setter
    def appname(self, value):
        with self._tdlock:
            self._appname = value

    @property
    def version(self):
        with self._tdlock:
            return self._version

    @version.setter
    def version(self, value):
        with self._tdlock:
            self._version = value

    @property
    def config__metadata(self):
        class Configmetadataproxy:
            def __init__(proxyself, configmetadata, lock):
                proxyself._configmetadata__ = configmetadata
                proxyself._threadlock = lock

            def __getitem__(proxyself, key):
                with proxyself._threadlock:
                    if key in proxyself._configmetadata__:
                        return proxyself._configmetadata__[key]
                    else:
                        raise KeyError(f"Key '{key}' not found in config metadata.")

            def __setitem__(proxyself, key, value):
                with proxyself._threadlock:
                    if key in proxyself._configmetadata__:
                        proxyself._configmetadata__[key] = value
                    else:
                        raise KeyError(f"Key '{key}' not found in config metadata.")

            def __repr__(proxyself):
                with proxyself._threadlock:
                    return repr(proxyself._configmetadata__)
        return Configmetadataproxy(self._configmetadata, self._tdlock)

    @property
    def dependantnodes(self):
        with self._tdlock:
            # Return a shallow copy to prevent external modification
            return dict(self._dependantnodes)

    @dependantnodes.setter
    def dependantnodes(self, value: object) -> None:
        with self._tdlock:
            self._dependantnodes = value
    
    @property
    def flaskapp(self) -> t.Type[Flask]:
        with self._tdlock:
            return self._flaskapp
    
    @flaskapp.setter
    def flaskapp(self, value: t.Type[Flask]) -> None:
        with self._tdlock:
            self._flaskapp = value
    
    @property
    def transactionCode(self)->str:
        with self._tdlock:
            return self._txnCode
    
    @transactionCode.setter
    def transactionCode(self,value:str)->None:
        with self._tdlock:
            self._txnCode = value
    
    @property
    def transactionMethod(self)->str:
        with self._tdlock:
            return self._txnMethod
    
    @transactionMethod.setter
    def transactionMethod(self,value:any)->None:
        with self._tdlock:
            self._txnMethod = value
        
    @property
    def clientAddress(self)->any:
        with self._tdlock:
            return self._clientaddress
        
    @clientAddress.setter
    def clientAddress(self,value:any)->None:
        with self._tdlock:
            self._clientaddress = value
    
    @property
    def logsConfig(self)->dict:
        with self._tdlock:
            # Return a shallow copy to prevent external modification
            return dict(self._logsconfig)
    
    @logsConfig.setter
    def logsConfig(self,value:dict)->None:
        with self._tdlock:
            self._logsconfig = value
        
    @property
    def externalConfig(self)->any:
        with self._tdlock:
            return self._externalcfg
    
    @externalConfig.setter
    def externalConfig(self,value:any)->None:
        with self._tdlock:
            self._externalcfg = value
    
    @property
    def registeredDynastComponents(self)->list:
        with self._tdlock:
            # Return a copy to prevent external modification
            return list(self._registeredDynastComponents)
    
    @registeredDynastComponents.setter
    def registeredDynastComponents(self,value:object)->None:
        with self._tdlock:
            self._registeredDynastComponents.append(value)
    
    @property
    def applicationResources(self) -> object:
        """
        Returns resources object which holds resources in each service as dynamically setted objects .
        """
        with self._tdlock:
            return self._resources
        
    @applicationResources.setter
    def applicationResources(self, value: object) -> None:
        """
        Sets the resources object which holds resources in each service as dynamically setted objects.
        """
        with self._tdlock:
            self._resources = value
            
    @property
    def applicationLogs(self) -> any:
        """
        Returns the application logs object.
        """
        with self._tdlock:
            return self._applicationLogs
        
    @applicationLogs.setter
    def applicationLogs(self, value: any) -> None:
        """
        Sets the application logs object.
        """
        with self._tdlock:
            self._applicationLogs = value
    @property
    def configManagerMap(self) -> dict:
        """
        Returns the config manager map.
        """
        with self._tdlock:
            return self._cfgmanager
        
    @configManagerMap.setter
    def configManagerMap(self, value: any) -> None:
        """
        Sets the config manager map.
        """
        with self._tdlock:
            self._cfgmanager.update(value)
            
    @property
    def mpath(self) -> str:
        """
        Returns the main path of the application.
        """
        with self._tdlock:
            return self._mpath if self._mpath else DependantConstants.mpathdefault

    @mpath.setter
    def mpath(self, value: str) -> None:
        """
        Sets the main path of the application.
        """
        with self._tdlock:
            self._mpath = value

    @property
    def svspath(self) -> str:
        """
        Returns the services path of the application.
        """
        with self._tdlock:
            return self._svspath if self._svspath else DependantConstants.svspathdefault

    @svspath.setter
    def svspath(self, value: str) -> None:
        """
        Sets the services path of the application.
        """
        with self._tdlock:
            self._svspath = value
    @property
    def servicesabspath(self) -> str:
        """
        Returns the absolute path of the services.
        """
        with self._tdlock:
            return self._servicesabspath
    
    @servicesabspath.setter
    def servicesabspath(self, value: str) -> None:
        """
        Sets the absolute path of the services.
        """
        with self._tdlock:
            self._servicesabspath = value 
            
    @property
    def applicationparentpath(self) -> str: 
        """
        Returns the parent path of the application.
        """
        with self._tdlock:
            return self._applicationparentpath
    
    @applicationparentpath.setter
    def applicationparentpath(self, value: str) -> None:
        """
        Sets the parent path of the application.
        """
        with self._tdlock:
            self._applicationparentpath = value