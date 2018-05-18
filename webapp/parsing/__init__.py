import re
import datetime
from webapp import models
from webapp.app_init import db
import logging
from webapp import parsing_plugins
from flask.views import MethodView

logger = logging.getLogger(__name__)
# print('__name__', __name__)
DATE_HEADER_PATTERN = re.compile(r"^[0-9]+-[0-9]+-[0-9]*\w*$")


def datestr(y: str, m: str, d: str) -> str:
    a = leftpad(y, 4, "0")
    b = leftpad(m, 2, '0')
    c = leftpad(d, 2, '0')
    return '-'.join((a, b, c))


def leftpad(s: str, l: int, c=' ') -> str:
    if l > len(s):
        return c * (l - len(s)) + s
    return s


class Entry:

    def __init__(self, date: datetime.date, body: str):
        self._date = date
        self._body = body

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def date_string(self) -> str:
        return self._date.strftime("%Y-%m-%d")

    @property
    def body(self) -> str:
        return self._body

    def __repr__(self):
        return "Entry(date='{}',body=\"{}\")".format(self.date, self.body)

    def __eq__(self, other):
        return self._date == other._date and self._body == other._body


def identify_entries(lines) -> "list[Entry]":
    cur_body_lines = []
    old_date = None
    a = b = c = 0
    results = []
    d = None
    each_line = None
    for each_line in lines:
        if DATE_HEADER_PATTERN.search(each_line):
            try:
                a, b, c = map(int, old_date.split("-"))
                d = datetime.datetime(a, b, c, 0, 0)
            except (ValueError, AttributeError):
                d = None
            if len(cur_body_lines) > 0 and d is not None:
                results.append(Entry(d, '\n'.join(cur_body_lines)))
            if not old_date:
                old_date = each_line

            cur_body_lines = []
            old_date = each_line
        else:
            cur_body_lines.append(each_line)
    if old_date is not None:
        d = old_date
    else:
        d = each_line
    try:
        d = (
            datetime.datetime(*(list(map(int, old_date.split("-"))) + [0, 0])))
    except AttributeError:
        raise ValueError(f"Error parsing journal. Invalid date: '{d}'")
    b = '\n'.join(cur_body_lines)
    if d is not None and len(b) > 0:
        results.append(Entry(d, b))
    return results


class Plugin:
    """Ancestor class for plugins related to parsing
    and recognizing rich content within Entry(s)."""
    requires_initialization = True
    initialized = False

    @classmethod
    def get_class_name(cls):
        """Return the name of this class including the file in which it is defined."""
        s = str(cls).split(' ')[1]
        return s[1:-2]

    @classmethod
    def get_unique_name(cls):
        """Return the name of this class including the file in which it is defined."""
        s = cls.get_class_name()
        return s.split('.')[0]

    def __init__(self):
        self.logger = logger.getChild(self.name.replace(' ', '_').lower())
        plugin_class = self.__class__

        class DefaultPluginView(MethodView):
            def get(self):
                return f'Hello, this is the default plugin view for {plugin_class.get_unique_name()}!'

        self._view = DefaultPluginView
        self.base_url = '/plugin/' + plugin_class.get_unique_name()

    def get_model(self):
        """Return the databse record associated with this plugin."""
        found = db.session.query(models.PluginConfig).filter(
            models.PluginConfig.class_name == self.get_class_name()).first()
        return found

    def init(self):
        """The responsibility of this method is to perform long-running
        initialization tasks such as downloading resources,
        building large data structures to be read later, etc.
        It is distinct from __init__ in this respect."""
        self.initialized = True
        raise NotImplementedError("init() not implemented.")

    def parse_entry(self, e: Entry) -> list:
        """Return a list of objects found in the Entry."""
        if self.requires_initialization and not self.initialized:
            raise RuntimeError("This classes resources must be initialized!")
        raise NotImplementedError("parse_entry() not implemented!")

    def bootstrap_endpoint_onto_app(self, base_endpoint: str, app):
        base = '/'.join([t for t in base_endpoint.split('/') if len(t) > 0])
        url = f'/{base}/{self.get_unique_name()}'
        self.base_url = url
        app.add_url_rule(url,
                         view_func=self.view.as_view(f'plugin.{self.get_unique_name()}.index'))

    @property
    def enabled(self):
        return self.get_model().enabled

    @enabled.setter
    def enabled(self, val):
        m = self.get_model()
        m.enabled = val
        db.session.add(m)
        db.session.flush()
        db.session.commit()

    @property
    def view(self):
        return self._view

    @property
    def url(self):
        return self.base_url


class PluginManager:
    registered_plugins = list()  # 'List[Plugin]'
    plugins_by_unique_name = {}
    name = 'Plugin'

    @classmethod
    def register(cls, plugin_class: Plugin):
        assert not logger.disabled
        logger.debug('Register plugin "%s"', plugin_class.name)
        cls.registered_plugins.append(plugin_class())

    @classmethod
    def init(cls):
        # track plugin configurations in db
        for p in cls.registered_plugins:
            found = db.session.query(models.PluginConfig).filter(
                models.PluginConfig.class_name == p.get_class_name()).first()
            if found is None:
                # unique name based on filename
                found = models.PluginConfig(class_name=p.get_class_name())
                found.enabled = True
            # human name
            found.name = p.get_class_name()
            db.session.add(found)
            db.session.flush()
            db.session.commit()
        for p in cls.registered_plugins:
            try:
                p.init()
            except NotImplementedError:
                pass

    @classmethod
    def parse_entry(cls, e: Entry) -> 'generator[tuple]':
        """Return a dictionary mapping each registered
        plugin to the results of it parsing the target Entry."""
        for p in cls.registered_plugins:
            found = db.session.query(models.PluginConfig).filter(
                models.PluginConfig.class_name == p.get_class_name()).first()
            if found.enabled:
                items = list(p.parse_entry(e))
                if items:
                    yield (p, items)


parsing_plugins.init(PluginManager)
