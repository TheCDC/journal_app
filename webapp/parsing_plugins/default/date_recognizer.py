"""An example plugin that identifies dates of a particular format
found in the journal entries."""
from webapp import parsing
from webapp import models
from webapp import api
import parsedatetime as pdt
print(__name__)
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
        cls.logger.debug(e)
        cal = pdt.Calendar()
        for t in cal.nlp(e.contents, e.create_date.timetuple()):
            found_date = api.strip_datetime(t[0])
            if found_date not in seen and api.entry_exists(found_date):
                original_case = t[-1]
                # get a link to the entry referred to by the found date
                url = api.link_for_date(
                    year=found_date.year,
                    month=found_date.month,
                    day=found_date.day)
                # plugins may return HTML.
                yield f'''<a href="{url}">
                {original_case}
                ({found_date.year}-{found_date.month}-{found_date.day})
                </a>'''

                seen.add(found_date)
