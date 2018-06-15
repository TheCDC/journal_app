from webapp.journal_plugins.classes import PluginReturnValue

def validate(func):
    def wrapped(*args,**kwargs):
        gen = func(*args,**kwargs)
        for item in gen:
            try:
                yield PluginReturnValue(**item).dict
            except ValueError as e:
                raise e


    return wrapped