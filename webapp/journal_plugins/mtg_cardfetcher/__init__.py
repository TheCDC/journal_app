"""This module is an example of making a plugin.

It identifies capitalized words in the text of journal entries."""
from webapp import app
from webapp.journal_plugins import classes
from . import views, models

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
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

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
        updated_at = datetime.datetime.now()
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


class Plugin(classes.BasePlugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Magic: the Gathering Fetcher'
    description = 'Identify Magic: The Gathering cards you mention in your entries.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = []
        self.cards_file_path = os.path.join(self.resources_path, 'cards.json')
        self.thread = threading.Thread(target=fetch, kwargs=dict(mailbox=self.queue, target=self.cards_file_path))
        self.thread.start()
        self.card_matcher = None
        self.manager.blueprint.add_url_rule(self.endpoint,
                                            view_func=views.IndexView.as_view(f'{self.url_rule_base_name}-index'))

    def _parse_entry(self, e: 'webapp.models.JournalEntry') -> 'iterable[str]':
        if self.card_matcher is None:
            if self.thread.isAlive():
                return
            else:
                try:
                    self.card_matcher = self.queue.pop()
                except IndexError:
                    logging.warning('This literally shouldn\'t happen. The thread is dead but the mailbox is empty?!')
                    logging.warning(self.queue)
        else:
            found = identify_cards(e.contents, self.card_matcher)
            for cardname in found:
                yield link_element_template.format(link=base_url + '&quot ' + '+'.join(cardname.split(' ')) + '&quot',
                                                   body=cardname)

    def parse_entry(self, e: 'webapp.models.JournalEntry') -> 'iterable[str]':

        found = models.MTGCardFetcherCache.query.filter(models.MTGCardFetcherCache.parent == e).first()

        if found:
            # try to get the session the object is already in
            session = db.session.object_session(found)
            # if it isn't in a session, make a new onw
            if session is None:
                session = db.session()

            found_obj = json.loads(found.json)
            if (found.updated_at < e.updated_at or len(found_obj) < 0):

                results = list(self._parse_entry(e))
                found.json = json.dumps(results)
                session.add(found)
                session.commit()

            else:
                results = json.loads(found.json)

            return results
        else:
            results = list(self._parse_entry(e))
            found = models.MTGCardFetcherCache(parent=e, json=json.dumps(results))
            session = db.session.object_session(e)
            if not session:
                session = db.session()
            session.add(found)
            session.commit()
            return results
