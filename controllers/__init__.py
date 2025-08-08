# the controller
from flaskmate.modules.app.Application import CGInvoker
from flaskmate.modules.app.DependantConstants import DependantConstants
from flaskmate.types import FlaskMateAppType
import os,inspect
import click

dependantconstants=DependantConstants()

class CGAppController(CGInvoker):
    #This class controls the class Application and is responsible for initializing the framework and providing access to its components.
    #It is also responsible for providing the application object and running the application. All flow will be controlled here
    """
        FlaskMate is a web development framework for building scalable and maintainable applications using Flask.
    """
    def __init__(self,appname, externals:any = None )->CGInvoker:
        click.echo(f"Initializing Application {appname}. Finding root path...")
        dependantconstants.root_path = self._getroot_()
        click.echo(f"Detected root path {dependantconstants.root_path}")
        super().__init__(appname)
    
    def _getroot_(self)->str:
        """
        Get the root path of the application
        """
        _caller_frame = inspect.stack()[2]
        _caller_file = _caller_frame.filename
        self._calledpath = os.path.dirname(os.path.abspath(_caller_file))
        return self._calledpath
    
