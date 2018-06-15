from webapp.journal_plugins.classes import PluginReturnValue

def validate(func):
    def wrapped(*args,**kwargs):
        gen = func(*args,**kwargs)
        for item in gen:
            yield dict(PluginReturnValue(item))

    return wrapped