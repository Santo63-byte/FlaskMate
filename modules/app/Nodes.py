from flaskmate.modules.app.DependantConstants import DependantConstants
from flaskmate.modules.app.Addons import CGApplicationAddons
from flaskmate.modules.orchestration.exceptions import CGImportError
from flaskmate.types import NodeType
from flaskmate.modules.app.abstracts import NodeAbstract
from flaskmate.modules.utils.enhancers.colors import CGEnhancers as bcolors
from typing import Type,Literal,Optional,Callable,override
import importlib,click
from flask import Flask
import pkgutil
import os,time
import logging

applogger=logging.getLogger('app')
dependants=DependantConstants()

C="CORS"
S="SECURITY"
D="DATABASE"

class NodeComponent(NodeAbstract):
    """
    The Node Parent Class 
    """
    def __init__(self,node:Type[object],instance,name,author,description,cross_origins)->None:
        self.__module__ = " cgframework.modules.app.nodecomponent "
        self.__name__ = " CGNodeComponent "
        self.__doc__ = " The parent component of nodes "
        self._instance=instance
        self._name=name
        self._author=author
        self._description=description
        self._cross_origins=cross_origins
        self._node = node
        self._nodestructure={
            "name": self._name,
            "author": self._author,
            "type": None,
            "description": self._description,
            "cors": None,
            "instance": None
        }
        
    @override
    def _append_node_(self,node:Type[object])->None:
        """
        Append the node to the node component.
        """
        pass
    
    @override
    def construct_node(self,nodetype:NodeType="dynast_node")->dict[str,any]:
        """
        Construct the node to the node component. For each node type, the method will be called to construct the node structure for dynast and entry nodes it will be different and can be implemented independently below 
        elow are just initial implementations
        """
        if nodetype == "entry_node":
            self._nodestructure.get("type",nodetype)
            return self._nodestructure
            
        elif nodetype == "dynast_node":
            self._nodestructure["type"]=nodetype
            self._nodestructure["instance"]=self._instance
            self._nodestructure["cors"]=self._cross_origins
            return self._nodestructure
        
        else:
            raise Exception("Invalid node type")

    # @override
    # def initializeaddons(self, addontype:str, *args, **kwargs)->None:
    #     addons={
    #         "CORS": CGApplicationAddons.handle_cross_browser_requests,  
    #     }
    #     if addontype in addons:
    #         click.echo(f"Initializing {addontype} addons for the node component")
    #         addons[addontype](*args, **kwargs)
    #     else:
    #         raise Exception(f"FlaskMate internal error. Addon type {addontype} not found in the addons list. Available addons are {addons.keys()}")
        

class EntryNode(NodeComponent):
    
    """Entry Node will have only one entry class which will be called after running the application"""
    def __init__(self,node:Type[object]=None)->None:
        
        self.__module__ = "cgframework.modules.app.entrynode"
        self.__name__ = "CGEntryNode"
        self.__doc__ = "Entry node class for the CGFramework."
        self._append_node_(node)
        
    def _append_node_(self,node:Type[object])->None:
        """
        Append the node to the entry node.
        """
        dependants.dependantnodes['entrynode'] = node
        
    @staticmethod    #to be accessed across all other objects
    def _get_entry_node_()->Type[object]:
        """ 
        Get the entry node.
        """       
        return dependants.dependantnodes.get('entrynode',None)
    
    @staticmethod
    def check_entry_node()->Optional[Callable[[Flask], None]]:
        """
        Handle the entry node by checking if it is registered in the dependants.
        If it is registered, return the entry node instance.
        If not, return None.
        """
        applogger.info('Checking for Entry Node')
        entry_node_instance: Optional[Callable[[Flask], None]] = EntryNode._get_entry_node_()
        if entry_node_instance:
            applogger.info(f'Entry Node {entry_node_instance} found.')
            return entry_node_instance
        else:
            applogger.warning(f'{bcolors.WARNING}Entry Node not found. Provided entry node is {entry_node_instance}{bcolors.RESET}.')
            return None
        
    @staticmethod
    def initialize_entry_node(appinstance:Type[object])->None:
        """
        Initialize the entry node.
        """
        node_instance: Optional[Callable[[Flask], None]] = EntryNode._get_entry_node_()
        if node_instance:
            applogger.info(f'Detected Entry Node {node_instance}.')
            try:
                node_instance(appinstance)
            except Exception as e:
                applogger.error(f'{bcolors.FAIL}Error initializing Entry Node {node_instance}: {e}{bcolors.RESET}')
                raise SystemError(f'Error initializing Entry Node {node_instance}: {e}')
        else:
            applogger.warning(f'{bcolors.WARNING}Entry Node not found. Provided entry node is {node_instance}{bcolors.RESET}.')

          
class DynastNodes(NodeComponent):
    """
        Service Node should have the list of controllers for each services and application object will be injected to each controller's constructor
            
            Dynast Structure
            {
                "name": "ModelInvokerController",
                "author": "John Doe",
                "type": "dynast",
                "description": "Structure of {name} Dynast component.",
                "cors": ["abcd.com", "xyz.com"],
                "instance": "classinstance"
            }

    """
    def __init__(self,node:Type[object],classinstance:object,name:str,author:str,desc:str,cross_origins:list[str])->None:
        
        self.__module__ = "cgframework.modules.app.dynastnode"
        self.__name__ = "CGDynastNodes"
        self.__doc__ = "Dynast node class for the CGFramework."
        super().__init__(node=node,instance=classinstance,name=name,author=author,description=desc,cross_origins=cross_origins)
    
    def construct(self)->None:
        """
        Construct the node to the dynast node.
        """
        dynast_node:dict[str,any]=self.construct_node("dynast_node")
        self.append_dynast(dynast_node)
    
    def append_dynast(self,classinstance:Type[object])->None:
        """
        Append the node to the service node.
        """
        if(classinstance is None):
            raise Exception("Dynast node class instance cannot be None")
        dependants.registeredDynastComponents = classinstance
        
    @staticmethod
    def get_dynasts()->Type[object]:
        """ 
        Get the service node.
        """       
        return dependants.registeredDynastComponents
    
            
class NodeScanner:
    """""Node Scanner class to scan the nodes and trigger the decorators to put instances into register object.
    """
    def __init__(self,app,**args)->None:
        self.appinstance= app
     
    def initialize(self)->None:
        
        #Initially importing the modules to trigger the decorators (the below two lines will be replaced with the actual module import handler)
        self.scanpathconfigurations= dependants.config__metadata['dynastnodes'] if dependants.config__metadata['dynastnodes'] else None
        self.module_import_handler(self.scanpathconfigurations)
        # When starting system should find if Entry Node presence is there or not
        click.echo('********************************************************************************')
        entry_node_instance: Optional[Callable[[Flask], None]] = EntryNode.check_entry_node() # check if entry node is registered in the dependant application
        
        if entry_node_instance:
            EntryNode.initialize_entry_node(self.app)
            applogger.warning(f"{bcolors.WARNING}Entry Node is detected. Hence skipping the DynastNode initialization. Route Initialization will be done by the Entry Node{bcolors.RESET}")
            return
        
        time.sleep(1)
        click.echo('********************************************************************************')
        # For annotation instance scanning, (these include DynastNode, upcoming annotations..) will be scanned and initialized
        """
        Initialize the dynast nodes.
        First the method check for whether the dynast module configurations are provided or not
        If yes the scanning will be reduced to the provided configurations else whole scan will be done( which is the default and recommended but will affect the intital loading performance)
        """
        applogger.info("Initializing the Dynast nodes")
        detected_dynasts:list[object]=dependants.registeredDynastComponents
        if detected_dynasts is None or detected_dynasts == []:
            applogger.warning(f"{bcolors.WARNING}No Dynast nodes detected. Please check the dynast module configurations in your application{bcolors.RESET}")
            return
        for dynast in detected_dynasts:
            applogger.info("Running through detected Dynast nodes")
            try:
                dynast['instance'](self.appinstance)
            except Exception as e:
                applogger.error(f"{bcolors.FAIL}Error initializing Dynast node {dynast}: {e}{bcolors.RESET}")
                
    
    def module_import_handler(self,configurations:Optional[any]=None)->None:
        """
        Handles the import of the modules to trigger the Annotations
        
        # TO DO - Add the logic to handle the module import without the need of configurations
        """
        moduleslist:list[str] = []
        
        # Check if configurations exist and is not empty
        if configurations and isinstance(configurations, dict):
            # Iterate through each service in the configurations
            for service_name, controller_paths in configurations.items():
                for module_path in controller_paths:
                    if module_path and module_path.lower() != 'none':
                        moduleslist.append(module_path)
        
        # Now scan each valid module path
        for module_path in moduleslist:
            self.scan_nodes(module_path)
            
    def scan_nodes(self,module_path:str)->None:
        """
        Scan the nodes and trigger the decorators to put instances into registered object.
        Recursively imports all .py files within the module path.
        """
        try:
            applogger.info(f"Scanning  nodes in {module_path}")
            base_module = importlib.import_module(module_path)
        
            if hasattr(base_module, '__path__'):
                package_path = base_module.__path__
            elif hasattr(base_module, '__file__'):
                package_path = [os.path.dirname(base_module.__file__)]
            else:
                applogger.warning(f"{bcolors.WARNING}Cannot determine path for module {module_path}{bcolors.RESET}")
                return
            for _, submodule_name, is_pkg in pkgutil.walk_packages(package_path):
                full_submodule_name = f"{module_path}.{submodule_name}"
                applogger.info(f"Importing submodule: {full_submodule_name}")
                try:
                    importlib.import_module(full_submodule_name)
                except Exception as e:
                    applogger.error(f"{bcolors.FAIL}Error importing submodule {full_submodule_name}: {str(e)}{bcolors.RESET}")
                    
        except CGImportError as e:
            applogger.error(f"{bcolors.FAIL}Error importing module {module_path}: {e}{bcolors.RESET}")
        except Exception as e:
            applogger.error(f"{bcolors.FAIL}Error scanning module {module_path}: {e}{bcolors.RESET}")