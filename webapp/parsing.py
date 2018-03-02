import re
import datetime
DATE_HEADER_PATTERN = re.compile(r"^[0-9]+-[0-9]+-[0-9]*\w*")


def datestr(y, m, d):
    a = leftpad(y, 4, "0")
    b = leftpad(m, 2, '0')
    c = leftpad(d, 2, '0')
    return '-'.join((a, b, c))


def leftpad(s, l, c=' '):
    if l > len(s):
        return c * (l - len(s)) + s
    return s


class Entry:
    def __init__(self, date: datetime.date, body: str):
        self._date = date
        self._body = body

    @property
    def date(self):
        return self._date
    @property
    def date_string(self):
        return self._date.strftime("%Y-%m-%d")

    @property
    def body(self):
        return self._body

    def __repr__(self):
        return "Entry(date='{}',body=\"{}\")".format(self.date, self.body)

    def __eq__(self, other):
        return self._date == other._date and self._body == other._body


def identify_entries(lines):
    cur_body_lines = []
    old_date = None
    a = b = c = 0
    results = []
    _x = None
    d = None
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
        d = (datetime.datetime(*(list(map(int, old_date.split("-"))) + [0, 0])))
    else:
        d = each_line
    b = '\n'.join(cur_body_lines)
    results.append(Entry(d, b))
    return results
