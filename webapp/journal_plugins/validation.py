from webapp.journal_plugins.classes import PluginReturnValue

def validate(func):
    def wrapped(*args,**kwargs):
        gen = list(func(*args,**kwargs))
        if gen is None:
            return
        for item in gen:
            try:
                yield PluginReturnValue(**item).dict
            except Exception as e:
                raise ValueError(f'Function {func} has invalid output schema! Args: {args}, {kwargs}, {gen} Error: {e}')


    return wrapped