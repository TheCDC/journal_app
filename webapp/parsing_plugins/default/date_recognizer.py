"""An example plugin that identifies dates of a particular format
found in the journal entries."""
from webapp import parsing
from webapp import models
import webapp
import re
import datetime


# ========== Regex and parsing stuff  ==========
def parse_date_string(s: str):
    tokens = s.split('-')
    year = int(tokens[0])
    month = int(tokens[1])
    day = int(tokens[2])
    return datetime.datetime(year, month, day)


# regex => date described by match
patterns = [
    (r'[0-9]+-[0-9]+-[0-9]+', (lambda d, s: (parse_date_string(s)))),
    (r'yesterday', (lambda d, s: d - datetime.timedelta(1))),
    (r'tomorrow', lambda d, s: d + datetime.timedelta(1)),
]
# compile all regexes together to eliminate overlap
compiled_patterns = [(re.compile(t[0]), t[1]) for t in patterns]
pattern_string = '|'.join(t[0] for t in patterns)
all_patterns = re.compile(pattern_string)

# ========== Plugin Class  ==========


class Plugin(parsing.Plugin):
    """This class is the entry point of the module
    with respect to the plugin system.

    Finds dates mentioned in entries."""
    name = 'Date Recognizer'

    @classmethod
    def parse_entry(cls, e: models.JournalEntry) -> 'iterable[str]':
        """Find all dates mentioned in the entry body."""
        seen = set()
        # find all dates mentioned in the entry
        for f in all_patterns.finditer(e.contents.lower()):
            # aliases
            match = f.group(0)
            span = f.span()
            if match in seen:
                continue
            else:
                seen.add(match)
            # save both the date of the entry and the capitalization
            # of the match portion
            original_date = e.create_date
            original_case = e.contents[span[0]:span[1]]
            found_date = None
            # check whether any patterns match
            # then identify the first pattern that matched.
            for c in compiled_patterns:
                if c[0].search(match):
                    found_date = c[1](original_date, match)
                    break
            # get a link to the entry referred to by the found date
            url = webapp.api.link_for_date(
                year=found_date.year,
                month=found_date.month,
                day=found_date.day)
            # plugins may return HTML.
            yield f'<a href="{url}">{original_case} ({found_date.year}-{found_date.month}-{found_date.day})</a>'
