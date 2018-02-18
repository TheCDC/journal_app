import re
import datetime
re_dict = {"date_header": re.compile(r"^[0-9]+-[0-9]+-[0-9]*\w*")}


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
    def body(self):
        return self._body

    def __repr__(self):
        return "Entry(date='{}',body=\"{}\")".format(self.date, self.body)


def identify_entries(lines):
    cur_body_lines = []
    old_date = None
    a = b = c = ''
    results = []
    _x = None
    for index, each_line in enumerate(lines):
        if re_dict["date_header"].search(each_line):
            if not old_date:
                print('start date', each_line)
                old_date = each_line
            # print(tuple(int(i) for i in cur_date.split("-") if len(i) > 0))
            a, b, c = map(int, old_date.split("-"))

            if _x and cur_body_lines:
                results.append(_x)
            _x = Entry(datetime.date(a, b, c), '\n'.join(cur_body_lines))
            cur_body_lines = []
            old_date = each_line
        else:
            cur_body_lines.append(each_line)
    d = (datetime.date(*(map(int, old_date.split("-")))))
    b = '\n'.join(cur_body_lines)
    results.append(Entry(d, b))
    return results
