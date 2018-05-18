"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import parsing
from webapp import models
import re
import scrython
import aiohttp

card_pattern = re.compile(r'\[\[[^\[^\].]*\]\]')
link_element_template = '<a target="_blank" href="{link}">{body}</a>'
base_url = 'https://scryfall.com/search?q='


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Magic: the Gathering Fetcher'

    @classmethod
    def parse_entry(cls, e: models.JournalEntry) -> 'iterable[str]':
        seen = set()
        cards = list(card_pattern.findall(e.contents))
        for card in cards:
            if card not in seen:
                seen.add(card)
                cardname = card[2:-2]
                yield link_element_template.format(link=base_url + '+'.join(cardname.split(' ')), body=cardname)
