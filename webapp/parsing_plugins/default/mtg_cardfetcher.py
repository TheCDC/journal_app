"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import parsing
from webapp import models
import re
import requests
import threading
import json
import io
import zipfile
import os
import datetime
import dateutil.parser
import logging
import ahocorasick
from flask.views import MethodView


link_element_template = '<a target="_blank" href="{link}">{body}</a>'
base_url = 'https://scryfall.com/search?q=!'

url = 'http://mtgjson.com/json/AllCards.json.zip'


def tokenize(s):
    return s.strip()


def download_cards_to_file(destination='resources/cards.json'):
    resp = requests.get(url, stream=True)
    myfile = io.BytesIO(resp.content)
    with zipfile.ZipFile(myfile) as myzip:
        with myzip.open('AllCards.json') as cardsfile:
            cards = json.load(cardsfile)
    with open(destination, 'w') as f:
        f.write(json.dumps(cards))


def fetch(mailbox, target):
    meta_path = os.path.join(os.path.dirname(target), 'meta.json')
    now = datetime.datetime.now()

    def update_timestamp():
        with open(meta_path, 'w') as meta_info_file:
            updated_at = now
            obj = {
                'updated_at': updated_at.isoformat()
            }
            meta_info_file.write(json.dumps(obj))

    try:
        with open(meta_path) as meta_info_file:
            meta_info = json.load(meta_info_file)
            updated_at = dateutil.parser.parse(meta_info['updated_at'])
    except FileNotFoundError:
        update_timestamp()
    td = datetime.timedelta(days=1)
    if (now - updated_at) > td or not os.path.exists(target):
        print('download cards db')
        logging.info('MTG database too old. Updating...')
        download_cards_to_file(target)
        update_timestamp()
    with open(target) as f:
        cards = json.load(f)
    A = ahocorasick.Automaton()
    for card in cards:
        A.add_word(card, card)
    A.make_automaton()
    mailbox.append(A)
    return


def identify_cards(s, card_matcher):
    seen = set()
    for match in card_matcher.iter(s):
        name = match[1]
        if name not in seen:
            seen.add(name)
            yield name

class MTGCardfetcherView(MethodView):
    def get(self):
        return 'MTG Cardfetcher Plugin'

class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Magic: the Gathering Fetcher'

    def __init__(self):
        super().__init__()
        self.queue = []
        self.cards_file_path = os.path.join(self.resources_path, 'cards.json')
        self.thread = threading.Thread(target=fetch, kwargs=dict(mailbox=self.queue, target=self.cards_file_path))
        self.thread.start()
        self.card_matcher = None
        self._view = MTGCardfetcherView

    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        if self.card_matcher is None:
            if self.thread.isAlive():
                yield "Card database being built."
                return
            else:
                try:
                    self.card_matcher = self.queue.pop()
                except IndexError:
                    print('This literally shouldn\'t happen. The thread is dead but the mailbox is empty?!')
                    print(self.queue)
        found = identify_cards(e.contents, self.card_matcher)
        for cardname in found:
            yield link_element_template.format(link=base_url + '&quot ' + '+'.join(cardname.split(' ')) + '&quot',
                                               body=cardname)
