"""Module to ensure settings.py exists.
Import all plugin modules found in  the subpackage `installed`
and register them with `webapp.parsing.PluginManager`."""

from webapp.parsing import PluginManager
import os
import glob
import importlib.util

mydir = os.path.dirname(__file__)
# tuples of (config file, original copy)
files = [(os.path.join(mydir, 'settings.py'),
          os.path.join(mydir, 'settings.py.template'))]

# instantiate config files from templates if they don't exist.
for t in files:
    if not os.path.isfile(t[0]):
        with open(t[0], 'w') as dest:
            with open(t[1]) as src:
                dest.write(src.read())

# find all installed plugins
ALL_PLUGINS = glob.glob(os.path.join(mydir, 'installed', '*.py')) + \
    glob.glob(os.path.join(mydir, 'default', '*.py'))

# dynamically import all installed plugins
for p in ALL_PLUGINS:
    name = os.path.basename(p)
    # skip the file that anchors the package
    if name != '__init__.py':
        spec = importlib.util.spec_from_file_location(f'{name}', p)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        # tell the manager to handle each plugin
        PluginManager.register(foo.Plugin)
