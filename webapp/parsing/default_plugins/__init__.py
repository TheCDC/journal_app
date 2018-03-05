from webapp import parsing


class ExamplePlugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""

    @staticmethod
    def parse_entry(e):
        yield from e.body.split(' ')
