"""An example plugin that identifies dates of a particular format
found in the journal entries."""
from webapp import models
from webapp import api
import parsedatetime as pdt
from webapp.journal_plugins import classes
from webapp.journal_plugins.validation import validate
from webapp.extensions import db
import logging
from . import views

logger = logging.getLogger(__name__)


def shorten_phrase(s, max_length=15):
    if len(s) > 10:
        return s[:10] + '...'
    else:
        return s


def prettify(date_obj):
    pretty = f'{date_obj.year}-{date_obj.month}-{date_obj.day}'
    return pretty


# ========== Plugin Class  ==========


class Plugin(classes.BasePlugin):
    """This class is the entry point of the module
    with respect to the plugin system.

    Finds dates mentioned in entries."""
    name = 'Date Recognizer'
    description = 'Identify dates you mention in your entries and link you to the entries you mentioned.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.blueprint.add_url_rule(self.endpoint,
                                            view_func=views.IndexView.as_view(f'{self.url_rule_base_name}-index'))
        logger.info('Registered MTG Cardfetcher plugin view with url %s', self.url)

    @validate
    def parse_entry(self, e: 'models.JournalEntry') -> 'iterable[str]':
        """Find all dates mentioned in the entry body."""
        logger.disabled = False
        seen = set()
        cal = pdt.Calendar()
        db.session.add(e)
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
        for date, date_str in grouped_dates.items():
            found_entry = models.JournalEntry.query.filter(models.JournalEntry.create_date >= date).order_by(
                models.JournalEntry.create_date).first()
            dates_group = ' | '.join(date_str)

            if not found_entry:
                yield dict(html=f'<del>{dates_group}: {prettify(date)}</del>', url='')
            else:
                # get a link to the entry referred to by the found date
                url = api.link_for_entry(
                    found_entry)
                # plugins may return HTML.

                if found_entry.create_date == date:
                    item = f'<a href="{url}">{dates_group}: {prettify(date)}</a>'

                else:
                    item = f'<a href="{url}">{dates_group}: <del>{prettify(date)} </del> ➤ {prettify(found_entry.create_date)}</a>'
                yield dict(html=item, url=url, )

                seen.add(found_date)
