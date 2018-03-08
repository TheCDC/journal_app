import re
import datetime
from webapp import models
from webapp.app_init import db
import sqlalchemy
DATE_HEADER_PATTERN = re.compile(r"^[0-9]+-[0-9]+-[0-9]*\w*")


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
    for index, each_line in enumerate(lines):
        if DATE_HEADER_PATTERN.search(each_line):
            try:
                a, b, c = map(int, old_date.split("-"))
                d = datetime.datetime(a, b, c, 0, 0)
            except (ValueError, AttributeError):
                d = None
            if cur_body_lines and d:
                results.append(Entry(d, '\n'.join(cur_body_lines)))
            if not old_date:
                print('start date', each_line)
                old_date = each_line
            # print(tuple(int(i) for i in cur_date.split("-") if len(i) > 0))

            cur_body_lines = []
            old_date = each_line
        else:
            cur_body_lines.append(each_line)
    if old_date is not None:
        d = (
            datetime.datetime(*(list(map(int, old_date.split("-"))) + [0, 0])))
    else:
        d = each_line
    b = '\n'.join(cur_body_lines)
    results.append(Entry(d, b))
    return results


class Plugin:
    """Ancestor class for plugins related to parsing
    and recognizing rich content within Entry(s)."""
    requires_initialization = True
    initialized = False

    @classmethod
    def get_model(cls):
        found = db.session.query(models.PluginConfig).filter(
            models.PluginConfig.class_name == str(cls)).first()
        return found

    @classmethod
    def init(cls):
        cls.initialized = True
        """The responsibility of this method is to perform long-running
        initialization tasks such as downloading resources,
        building large data structures to be read later, etc.
        It is distinct from __init__ in this respect."""
        raise NotImplementedError("init() not implemented.")

    @classmethod
    def parse_entry(cls, e: Entry) -> list:
        """Return a list of objects found in the Entry."""
        if cls.requires_initialization and not cls.initialized:
            raise RuntimeError("This classes resources must be initialized!")
        raise NotImplementedError("parse_entry() not implemented/")

    @property
    @classmethod
    def enabled(cls):
        return cls.get_model().enabled

    @enabled.setter
    @classmethod
    def enabled(cls, val):
        m = cls.get_model()
        m.enabled = val
        db.session.add(m)
        db.session.flush()
        db.session.commit()


class PluginManager:
    registered_plugins = list()
    name = 'Plugin'

    @classmethod
    def register(cls, p: Plugin):
        cls.registered_plugins.append(p)

    @classmethod
    def init(cls):
        # track plugin configurations in db
        for p in cls.registered_plugins:
            found = db.session.query(models.PluginConfig).filter(
                models.PluginConfig.class_name == str(p)).first()
            if found is None:
                # unique name based on filename
                found = models.PluginConfig(class_name=str(p))
            # human name
            found.name = p.name
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
                models.PluginConfig.class_name == str(p)).first()
            if found.enabled:
                yield (p, list(p.parse_entry(e)))
