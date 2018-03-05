"""Module to ensure settings.py exists.
Import all plugin modules found in 'installed/'"""

from webapp.parsing import PluginManager
import os
import glob
import importlib.util
mydir = os.path.dirname(__file__)
files = [(os.path.join(mydir, 'settings.py'),
          os.path.join(mydir, 'settings.py.template'))]

for t in files:
    if not os.path.isfile(t[0]):
        with open(t[0], 'w') as dest:
            with open(t[1]) as src:
                dest.write(src.read())

for p in glob.glob(os.path.join(mydir, 'installed', '*.py')):
    name = os.path.basename(p)
    if name != '__init__.py':
        print(f'found plugin: {p}')
        spec = importlib.util.spec_from_file_location(f'{name}', p)
        print(spec)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)

        PluginManager.register(foo.Plugin)

# for  modname in pkgutil.iter_modules(package.__path__):
#     print("Found submodule %s (is a package: %s)" % (modname, ispkg))
# module = __import__(f'{package.__name__}.{modname}',fromlist='dummy')
