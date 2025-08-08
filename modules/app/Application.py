# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------------
from flaskmate.modules.helpers import CGHelper
from flaskmate.modules.logs import CGLogInvoker
from flaskmate.modules.configs import CGConfigInvoker
from flaskmate.modules.logs.Tracer import ExceptionTracer
from flaskmate.modules.orchestration.cmpln import ModuleCompilationInvoker
from flaskmate.modules.utils.enhancers.colors import CGEnhancers, badgedisplay
from flaskmate.modules.app.DependantConstants import DependantConstants
from flaskmate.modules.orchestration.exceptions import CGInitializationError
from flaskmate.modules.orchestration.exceptions.cgexception import CGException
from flaskmate.modules.app.Nodes import NodeScanner
from flaskmate.modules.app.abstracts import FlaskMateApp
from flaskmate.modules.app.Resources import ResourceManager
from flaskmate.modules.configs.ApplicationConfigs import CustomConfigContext 
import os, sys, logging, uuid,time
import traceback
import click
from typing import Any, Dict, Optional, Type, Union, Callable, NoReturn, override
from flask import Flask, jsonify, request, g, Response
from werkzeug._reloader import run_with_reloader
from flaskmate.resources.app import app_default_configs, cgframework_properties
#--------------------------------------------------------------------------------------------------------
logger = logging.getLogger('app')

class CGApplication(Flask,FlaskMateApp):
    
    def __init__(self, app_name: str) -> None:
        self.dependantconstants = DependantConstants()
        self.dependantconstants.appname = app_name
        super().__init__(app_name,root_path=self.dependantconstants.root_path,)
        self._app: Optional[Flask] = None
        self._config: Optional[Dict[str, Any]] = None
        self._root: Optional[str] = None
        self._dependantappcfg: Optional[Dict[str, Any]] = None
        self._modulescfg: Optional[Dict[str, Any]] = None
        sys.excepthook = self.exceptionhook
        CGEnhancers.displaybanner(badge=f"{cgframework_properties['name']}::{cgframework_properties['version']}")
              
    def init(self) -> None:
        """
        Initialize the application and set the config skeleton
        """
        self._config: Optional[Dict[str, Any]] = self.dependantconstants.config__metadata if self.dependantconstants.config__metadata else None
        self._root: Optional[str] = self.dependantconstants.root_path if self.dependantconstants.root_path else None
        try:
            self._dependantappcfg: Dict[str, Any] = CGHelper.loadYaml(
                os.path.join(self.dependantconstants.root_path, self.dependantconstants.app_yml), 'r'
            )
            self.configwrapper()
            self.check_custom_overrideable_configs()
            
        except FileNotFoundError as e:
            click.echo(f"Config file {self.dependantconstants.app_yml} not found in the root path {self.dependantconstants.root_path}. Please provide configurations for application.")
            raise CGException(
                f"Config file {self.dependantconstants.app_yml} not found in the root path {self.dependantconstants.root_path}. Please check the provided configurations") from e
        try:
            module_path = os.path.join(self.dependantconstants.root_path, self.dependantconstants.modules_file)
            exists:bool= CGHelper.file_check(module_path)
            if exists:
                self._modulescfg: Dict[str, Any] = CGHelper.loadJSon(module_path, 'r')
            else:
                self._modulescfg = CGHelper.construct_modules(root=self.dependantconstants.root_path,mainpath=self.dependantconstants.mpath,servicefoldername= self.dependantconstants.svspath)
        except CGInitializationError as e:
            click.echo(f"Error loading modules file {self.dependantconstants.modules_file} in the root path {self.dependantconstants.root_path}.")
            
    def logworker(self) -> None:
        """
        Initialize the log worker for the application
        
        Args:
            type: The type of logger to initialize ('default' or any other value)
        """
        CGLogInvoker.default_log_invoker()
        CGLogInvoker.invoke()
    
    def configwrapper(self) -> None:
        """
        Wrapper for the config and set and override the config skeleton with provided values
        """
        configinvoker = CGConfigInvoker(dependantconfigs=self._dependantappcfg)
        configinvoker.invoke()
    
    def check_custom_overrideable_configs(self)->None:
        
        customizer=CustomConfigContext()
        customizer.detect_stackinfo()
        
    def cachepool(self) -> None:
        """
        Cachepool setter
        """
        pass
    def manage_resources(self) -> None:
        """
        Manage resources for the application
        """
        if (self.dependantconstants.config__metadata['application']['manage_resources'] == True):
            r = ResourceManager()
            try:
                r.perform()
            except Exception as e:
                click.echo(f"{CGEnhancers.FAIL}Error occurred while managing resources: {e}{CGEnhancers.RESET}")
                logger.error(f"Error occurred while managing resources: {e}")
            else:
                click.echo(f"{CGEnhancers.WARNING}Resource information not provide in the configurations of the application. Refer the documentation for more details.{CGEnhancers.RESET}")
        else:
            click.echo(f"{CGEnhancers.WARNING}Resource management is disabled in the application. Refer the documentation for more details.{CGEnhancers.RESET}")
    def compile(self,modulesconfig:Dict[str, Any]) -> None:
        """
    
        Compile the application and set the config skeleton with provided values
        """
        # Invoke the ModuleCompilationInvoker with the modules configuration to override the default compilation behavior and shutown lifecycle
        ci:object=ModuleCompilationInvoker(modules=modulesconfig)
        
        #as displaying compilation process is optional 
        if(self.dependantconstants.config__metadata['application']['compile_files'] == True):
            ci.invoke()
            
    def runapp(self, app: Flask) -> None:
        """
        Run the application and start the server
        
        Args:
            app: Flask application instance to run
        """
        def txn_handler(trnxtnprofile: str) -> None:
            """
            Transaction handler for the application
            Args:
                trnxtnprofile: Profile type for transaction handling
            """
            if trnxtnprofile == 'keep':
                @app.before_request
                def before_request() -> None:
                    """
                    Before request handler for the application
                    """
                    logger.info(f"Transaction started for the request {request.path}")
                    g.transaction_id = str(uuid.uuid4())
                    self.dependantconstants.transactionCode = g.transaction_id
                    g.request_method = request.method
                    self.dependantconstants.transactionMethod = request.method
                    g.client_address = request.remote_addr
                    self.dependantconstants.clientAddress = request.remote_addr
                    logger.info(f"Transaction ID: {g.transaction_id} for the request {request.path}")
                
                @app.after_request
                def after_request(response: Response) -> Response:
                    """
                    After request handler for the application
                    
                    Args:
                        response: Flask response object
                        
                    Returns:
                        Modified response with transaction ID header
                    """
                    response.headers['X-Transaction-ID'] = g.transaction_id
                    logger.info(f"Transaction ended for the request {request.path}")
                    g.transaction_id = None
                    g.request_method = None
                    g.client_address = None
                    return response
                @app.teardown_request
                def log_teardown_info(exception=None):
                    if exception:
                        error_trace = traceback.format_exc()
                        logger.error(f"Error during request teardown: {exception}\nTraceback:\n{error_trace}")
                    
        def apprunner(port: int, debug: bool, host: str) -> NoReturn:
            """
            Run the application and start the server
            
            Args:
                port: Port number to run the server on
                debug: Debug mode flag
                host: Host address to bind to
            """
            try:
                sys.excepthook = self.exceptionhook
                logger.info(f"App will start at port no:{port}")
                logger.warning(f"{CGEnhancers.OKCYAN}Note that {port} is the configured port to be served. It can be overrided by any other debugging configuration by the IDE you are using. Please check your debugging setup also if you can't make request to this mentioned port no:{port} or encountered with connection timeout issue{CGEnhancers.RESET}")
                # the below if condition need to check in next release
                if(debug or ( applicationconfig.get('monitor_change') == True) and (applicationconfig.get('compile_files') == True)):
                    if(debug):
                        logger.warning(f"{CGEnhancers.WARNING}App will run in debug mode{CGEnhancers.RESET}")
                        
                    def flaskrun() -> None:
                        # Check if files have changed and need recompilation
                        if applicationconfig.get('compile_files', True):
                            click.echo("Checking for changes in watched files...")
                            self.compile(self._modulescfg)
                        app.run(port=port, debug=False, host=host, load_dotenv=False, threaded=True)
                        
                    run_with_reloader(flaskrun, extra_files=applicationconfig.get('watch_files', []))
                else:
                    app.run(port=port, debug=debug, host=host, load_dotenv=False, threaded=True)
            except Exception as e:
                logger.error(f"{CGEnhancers.FAIL}Failed to start the Flask server: {e}{CGEnhancers.RESET}")
                sys.exit(1)
        
        if app is None:
            click.echo("Application instance not created. Please check the provided configurations")
            logger.error(f"{CGEnhancers.FAIL}Application instance not created. Please check the provided configurations{CGEnhancers.RESET}")
            sys.exit(1)
        else:
            applicationconfig: Dict[str, Any] = self.dependantconstants.config__metadata['application']
            port: int = applicationconfig.get('port', app_default_configs.get('port'))
            debug: bool = applicationconfig.get('debug', app_default_configs.get('debug'))
            host: str = applicationconfig.get('host', app_default_configs.get('host'))
            trnxtnprofile: str = applicationconfig.get('transaction_profile', app_default_configs.get('transaction_profile'))
            txn_handler(trnxtnprofile)
            # Starting the application
            apprunner(port=port, debug=debug, host=host)
            
    def getinstance(self) -> Flask:
        """
        Get the instance of the application and return the app object
        
        Returns:
            Flask application instance
        """
        self._appname: str = self.dependantconstants.appname
        self._app = Flask(self._appname)
        self.dependantconstants.flaskapp = self._app
        self._app.config['PROPAGATE_EXCEPTIONS'] = True
         
        def internal_server_error() -> tuple[Response, int]:
            return jsonify(
                "An unexpected error occurred while processing response. Please contact admin."
            ), 500

        def bad_request(error: Any) -> tuple[Response, int]:
            return jsonify(
                "Invalid request data. Please format and try again"
            ), 400
            
        self._app.register_error_handler(500, internal_server_error)
        self._app.register_error_handler(400, bad_request)
        return self._app
    
    def exceptionhook(self,exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Any) -> None:
        """
        Exception hook for sys.excepthook
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        ExceptionTracer(exc_value)()
        
    def node_initializer(self) -> None:
        """
        FlaskMate node intializer check with priorities like EntryNode > DynastNode > ServiceNode > 
        
        If the application provided with entry node then it will be initialized and flask app object will be passed to it (For simpler architecture ENtryNode is recommended),
        If the application has so many controller classes like architecture then it is preferee to use DynastNode and DYNASTS configuration should be provided
        in config.yml file so that component scan can be reduced to that specific module and in Dynast Classes constructor the app object will be passed to it
        By default the application will be initialized either EntryNode and DynastNode as of now
        """
        NodeScanner(app=self.app).initialize()
#--------------------------------------------------------------------------------------------------------
class CGInvoker(CGApplication):
    """
    Invoker class is used to find the called root, name etc and initialize the app using the parent CGApplication and return the app object
    """
    
    def __init__(self, appname: str, **args: Any) -> None:
        """
        Initialize the invoker with application name
        
        Args:
            appname: Name of the application
            args: Additional arguments
        """
        # Here need to initialize the app.log file 
        
        super().__init__(appname)
        self.app: Optional[Flask] = None
        self._startapp_()
        self.run()
           
    def run(self) -> None:
        """
        Runs the application
        """
        try:
            logger.info('Starting Application')
            self.app = self.getinstance()
            if self.app:
                self.node_initializer()
                self.runapp(self.app)
            else:
                logger.warning(f'{CGEnhancers.WARNING}Instance not created for the application. Suspecting internal error. Please check the provided configurations{CGEnhancers.RESET}')
                logger.warning(f'{CGEnhancers.WARNING}Might Throw Exceptions and lead to shutdown {CGEnhancers.RESET}')
                
        except Exception as e:
            logger.error(f'{CGEnhancers.FAIL}Exception occurred while starting the application. Hence shutting down the application{CGEnhancers.RESET}')
            logger.error(f"Exception details: {e}")
            raise CGException(
                "An error occurred when starting app by the invoker. Due to above mentioned errors") from e
    
    def _startapp_(self) -> None:
        """
        Start the application and return the app object
        The workers pipeline
        """
        try:
            self.init() 
            self.logworker()
            self.manage_resources()  
            if self._modulescfg:
                self.compile(self._modulescfg)
            else:
                framework_name = cgframework_properties['name']
                message = f"{CGEnhancers.WARNING}Modules file {self.dependantconstants.modules_file} not found in the root path {self.dependantconstants.root_path}. {framework_name} will skip module check and automatic downloads if needed.{CGEnhancers.RESET}"
                logger.warning(message)
            badgedisplay()
        except Exception as e:
            raise CGInitializationError("An error occurred when starting app by the invoker. Due to above mentioned errors") from e