from flaskmate.modules.app.abstracts import Manager
import click
import os
from flaskmate.modules.helpers import CGHelper as cgh

class ResourceManager(Manager):
    """
    A class to manage resources for the application.
    This can include setting up resource pools from given configurations.
    """
    
    def __init__(self):
        """
        The ResourceManager worker is responsible for managing resources for the application.
        It initializes the resource manager and prepares to manage resources based on the application's configuration.
        """
        super().__init__()
        self.resources_datamap = {}
        
    def construct_resource_map(self) -> dict[str, tuple]:
        """
        Construct a resource map based on the application's configuration.
        :return: A dictionary representing the resource map.
        """
        config_resources = self.dependants.config__metadata['resources'] if self.dependants.config__metadata['resources']else {}
        resource_map = {}
        for key, cfg in config_resources.items():
            name = cfg.get('name')
            resource_dir = cfg.get('resource', 'resources')
            fmt = cfg.get('format')
            path_cfg = cfg.get('path')
            # Determine base directory
            if name and name.startswith('services.'):
                base = getattr(self.dependants, 'servicesabspath', '')
                # append module name after 'services.'
                mod_name = name.split('.', 1)[1]
                base = os.path.join(base, mod_name)
            else:
                base = getattr(self.dependants, 'applicationparentpath', '')
                if name:
                    base = os.path.join(base, name)
            # tO PROCESS PATH IF PRESENT
            if path_cfg:
                segments = path_cfg.split('.')
                base = os.path.join(base, *segments)
            file_name = f"{resource_dir}.{fmt}"
            full_path = os.path.join(base, file_name)
            resource_map[name] = (full_path, resource_dir, fmt)
        print(f"Constructed resource map: {resource_map}")
        return resource_map
    
    def validate(self):
        """
        Validate the resources to ensure they are correctly configured.
        """
        if (self.dependants.config__metadata['resources'] is None):
            self.validation_message ="No resources information provided. Skipping Resources scanning."
        else:   
            self.can_proceed() # setting proceed to True if provided resources are valid
        
    def execute(self) -> None:
        """
        Manage resources for the application.
        """
        self.resources = self.get_resource()
        self.load_resources(self.resources)
        # self.cache_resources() TD: after cacheing is implemented in the system
        
    def get_resource(self) -> object:
        """
        Get a specific resource by name.
    
        Args:
            resource_name: The name of the resource to retrieve.
        
        Returns:
            The requested resource object.
        """
        click.echo("Fetching resources from the configuration.")
        return self.construct_resource_map()

    def cache_resources(self, resource_name: str, resource: object) -> None:
        """
        Cache a resource for later use.
        
        Args:
            resource_name: The name of the resource to cache.
            resource: The resource object to cache.
        """
        pass
    
    def load_resources(self, resource_map:dict[str,tuple]) -> None:
        # Load resource files based on the resource map
        loaded = {}
        for name, (path, resource_dir, fmt) in resource_map.items():
            try:
                    if fmt.lower() == self.dependants.json:
                        data = cgh.loadJSon(path)
                        click.echo(f"Loaded and cached JSON resource '{name}' from '{path}'")
                    elif fmt.lower() in (self.dependants.yml):
                        data = cgh.loadYaml(path)
                        click.echo(f"Loaded and cached YAML resource '{name}' from '{path}'")
                    else:
                        click.echo(f"Unsupported resource format '{fmt}' for '{name}'. Supported formats are: {self.dependants.json}, {self.dependants.yml[0]}.")
                        continue
                    loaded[name] = data
            except Exception as e:
                click.echo(f"Failed to load resource '{name}' from '{path}': {e}")
        # Store loaded resource data
        print(f"Loaded resources: {loaded}")
        self.resources_datamap = loaded

    def unload_resources(self) -> None:
        """
        Unload resources when they are no longer needed.
        This can include closing connections, freeing memory, etc.
        """
        pass