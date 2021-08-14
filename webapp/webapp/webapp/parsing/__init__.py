import re
import datetime
import logging

logger = logging.getLogger(__name__)
DATE_HEADER_PATTERN = re.compile(r"^[0-9]+-[0-9]+-[0-9]+\s*$")


def datestr(y: str, m: str, d: str) -> str:
    a = leftpad(y, 4, "0")
    b = leftpad(m, 2, "0")
    c = leftpad(d, 2, "0")
    return "-".join((a, b, c))


def leftpad(s: str, l: int, c=" ") -> str:
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
    date = None
    for each_line in lines:
        if DATE_HEADER_PATTERN.search(each_line):
            e = Entry(date, "\n".join(cur_body_lines))
            if date is not None:
                results.append(e)

            a, b, c = map(int, each_line.split("-"))
            date = datetime.datetime(a, b, c, 0, 0)

            cur_body_lines = []
            old_date = each_line
        else:
            cur_body_lines.append(each_line)
    if date is not None and len(cur_body_lines) > 0:
        b = "\n".join(cur_body_lines)
        results.append(Entry(date, b))
    return results
