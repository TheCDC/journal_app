"""An example plugin that identifies dates of a particular format
found in the journal entries."""
from webapp import models
from webapp import api
import parsedatetime as pdt
from webapp.journal_plugins import classes
import logging
from . import views
logger = logging.getLogger(__name__)

def shorten_phrase(s, max_length=15):
    if len(s) > 10:
        return s[:10] + '...'
    else:
        return s


# ========== Plugin Class  ==========


class Plugin(classes.BasePlugin):
    """This class is the entry point of the module
    with respect to the plugin system.

    Finds dates mentioned in entries."""
    name = 'Date Recognizer'
    description = 'Identify dates you mention in your entries and link you to the entries you mentioned.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint, view_func=views.IndexView.as_view(f'{self.url_rule_base_name}-index'))
        logger.info('Registered MTG Cardfetcher plugin view with url %s', self.url)

    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        """Find all dates mentioned in the entry body."""
        logger.disabled = False
        seen = set()
        cal = pdt.Calendar()
        parsed_dates = cal.nlp(e.contents, e.create_date.timetuple())

        if parsed_dates is None:
            return

        grouped_dates = dict()
        for t in parsed_dates:
            found_date = api.strip_datetime(t[0])
            original_case = t[-1]
            human_strs = grouped_dates.get(found_date, [])
            human_strs.append(shorten_phrase(original_case))
            # print('original case', original_case)

            grouped_dates.update({found_date: human_strs})
        for date in grouped_dates:
            dates_group = ' | '.join(grouped_dates[date])
            pretty = f'''{dates_group}:
            ({date.year}-{date.month}-{date.day})'''

            if not api.entry_exists(date):
                yield f'<del>{pretty}</del>'
            else:
                # get a link to the entry referred to by the found date
                url = api.link_for_date(
                    year=date.year, month=date.month, day=date.day)
                # plugins may return HTML.
                yield f'<a href="{url}">{pretty}</a>'

                seen.add(found_date)
