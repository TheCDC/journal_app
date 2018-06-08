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
    meta_path = os.path.join(os.path.dirname(target),'meta.json')
    now = datetime.datetime.now()
    def update_timestamp():
        with open(meta_path,'w') as meta_info_file:
            updated_at = now
            obj = {
                'updated_at':updated_at.isoformat()
            }
            meta_info_file.write(json.dumps(obj))
    try:
        with open(meta_path) as meta_info_file:
            meta_info = json.load(meta_info_file)
            updated_at = dateutil.parser.parse(meta_info['updated_at'])
    except FileNotFoundError:
        update_timestamp()
    td = datetime.timedelta(days=1)
    if (now  - updated_at) > td or not os.path.exists(target):

        print('download cards db')
        logging.info('MTG database too old. Updating...')
        download_cards_to_file(target)
        update_timestamp()
    with open(target) as f:
        cards = json.load(f)
    print('start build re pattern')
    pattern = '(' + '|'.join(f'{re.escape(name)}'for name in cards) + ')'
    print(pattern)
    cards_patttern = re.compile(pattern)
    print('built re pattern')
    mailbox.append(cards_patttern)
    return


def identify_cards(s, cards_tree):
    seen = set()
    tokens = []
    for i, c in enumerate(tokenize(s)):
        tokens.append(c)
        tokens_t = tuple(tokens)
        found_cards = list(cards_tree.find_all(tokens))
        while len(found_cards) == 0 and len(tokens) > 0:
            # case of no cards possibly matching current search string
            tokens.pop(0)
            found_cards = list(cards_tree.find_all(tokens))

        if len(found_cards) == 1:
            # case of exactly one card matching current search string
            card = found_cards[0]
            p = tuple(card.get_phrase())
            if (len(p) == len(tokens)) and (p not in seen):
                seen.add(p)
                yield card


class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Magic: the Gathering Fetcher'

    def __init__(self):
        super().__init__()
        self.queue = []
        self.cards_file_path = os.path.join(self.resources_path, 'cards.json')
        self.thread = threading.Thread(target=fetch, kwargs=dict(mailbox=self.queue, target=self.cards_file_path))
        self.thread.start()
        self.cards_pattern = None

    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        if self.cards_pattern is None:
            if self.thread.isAlive():
                yield "Card database being built."
                return
            else:
                self.cards_pattern = self.queue.pop()
        found = list(self.cards_pattern.finditer(e.contents))
        print('found',found)
        seen = set()
        for cardname in found:
            cardname = cardname.group(1)
            if cardname not in seen:
                seen.add(cardname)
                print(cardname)
                yield link_element_template.format(link=base_url + '&quot '+ '+'.join(cardname.split(' ')) + '&quot', body=cardname)
        print(seen)
