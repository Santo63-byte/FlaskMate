from flask_cors import CORS
from flaskmate.types import FlaskMateAppType
from flaskmate.modules.app.abstracts import AddonsAbstracts
from typing import override

#TO be implemented in next version
class CGApplicationAddons(AddonsAbstracts):
    
    """
    This class is used to manage the addons for the CGApplication.
    This includes security features like CORS handling, authentications, session management and other application-specific addons.
    This class will take configurations from Application instance and apply to other service addons as needed.
    """

    def __init__(self):
        self.addons = []
        self.__qualname__ = self.__class__.__qualname__
        self._module= self.__module__
        self.__name__ = self.__class__.__name__
        self.__doc__ = "CGApplicationAddons class for managing application addons."
        self.__module__ = "cgframework.modules.app.addons"
        
    #For CORS handling
    @override
    @staticmethod
    def handle_cross_browser_requests(app:FlaskMateAppType, origins: list = None):
        """
        Handle cross-browser requests by applying CORS settings to the Flask application.
        
        :param app: The Flask application instance.
        :param origins: List of allowed origins for CORS. If None, defaults to allowing all origins.
        """
        CORS(app=app,resources=None,max_age=60000)