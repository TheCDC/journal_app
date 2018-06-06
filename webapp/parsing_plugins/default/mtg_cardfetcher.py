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
card_pattern = re.compile(r'\[\[[^\[^\].]*\]\]')
word_pattern = re.compile(r'\b[^\W_]+\b')
link_element_template = '<a target="_blank" href="{link}">{body}</a>'
base_url = 'https://scryfall.com/search?q=!'


class Node:

    def __init__(self, value):
        self.value = value
        self.children = list()
        self.parent = None

    def add_child(self, node):
        node.parent = self
        self.children.append(node)
        # self.children.sort(key=lambda n: n.value)

    def get_phrase(self):
        n = self
        ancestry = []
        while n.parent is not None:
            ancestry.insert(0, n.value)
            n = n.parent
        return ancestry

    def __str__(self):
        ancestry = self.get_phrase()
        return f'Node < "{self.value}", {len(self.children)} children >'
    def __hash__(self):
        return hash((self.value,))


class SuffixTree:

    def __init__(self, list_of_phrases, comparator=None):
        self.root = Node(None)
        self.memory = dict()
        if comparator:
            self.compare_function = comparator
        else:
            self.compare_function = lambda a, b: a == b
        for p in list_of_phrases:
            self.search(p, _insert=True)

    def search(self, list_of_words, _insert=False):
        """Return a tuple of (node, remaining_tokens).
        The search consumes tokens from list_of_words as it performs the search.
        Un-consumed tokens are return in remaining_tokens.
        """
        words_iter = iter(list_of_words)
        words_tuple = tuple(list_of_words)
        cur_token = next(words_iter)
        cur_node = self.root
        if words_tuple in self.memory:
            return self.memory[words_tuple]
        while True:
            # guard
            if len(cur_node.children) == 0 and not _insert:
                # memoize search and return value
                ret = (cur_node, list(words_iter))
                if words_tuple not in self.memory:
                    self.memory.update({words_tuple: ret})
                return self.memory[words_tuple]
            # check children for match
            for n in cur_node.children:
                if self.compare_function(n.value, cur_token):
                    cur_node = n
                    try:
                        cur_token = next(words_iter)
                    except StopIteration:
                        # memoize search and return value
                        ret = (cur_node, list(words_iter))
                        if words_tuple not in self.memory:
                            self.memory.update({words_tuple:ret})
                        return self.memory[words_tuple]
                    break
            else:
                # no matching children
                if not _insert:
                    return (cur_node, [cur_token] + list(words_iter))
                # make new node
                new_node = Node(cur_token)
                cur_node.add_child(new_node)
                cur_node = new_node
                try:
                    cur_token = next(words_iter)
                except StopIteration:
                    # memoize search and return value
                    ret = (cur_node, list(words_iter))
                    if words_tuple not in self.memory:
                        self.memory.update({words_tuple: ret})
                    return self.memory[words_tuple]
    def __str__(self):
        outlines = []
        d = 0
        stack = []
        stack.append((self.root, 0))
        while len(stack) > 0:
            cur = stack.pop()
            d = cur[1]
            outlines.append('  ' * d + str(cur[0]))
            for c in cur[0].children:
                stack.append((c, d + 1))
        return '\n'.join(outlines)

    def find_all(self, list_of_words):
        search_result = self.search(list_of_words)
        found_node = search_result[0]
        if found_node is self.root or len(search_result[1]) > 0:
            return
        stack = [found_node]
        while len(stack) > 0:
            cur = stack.pop()
            if len(cur.children) == 0:
                yield cur
            else:
                stack.extend(cur.children)


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
    try:
        with open(meta_path) as meta_info_file:
            meta_info = json.load(meta_info_file)
            updated_at = dateutil.parser.parse(meta_info['updated_at'])
    except FileNotFoundError:
        with open(meta_path,'w') as meta_info_file:
            updated_at = now
            obj = {
                'updated_at':updated_at.isoformat()
            }
            meta_info_file.write(json.dumps(obj))
    td = datetime.timedelta(days=1)
    if (now  - updated_at) > td or not os.path.exists(target):
        logging.info('MTG database too old. Updating...')
        download_cards_to_file(target)
    with open(target) as f:
        cards = json.load(f)
    cards_tree = SuffixTree([list(tokenize(name)) for name in cards], comparator=lambda a, b: a.lower() == b.lower())
    mailbox.append(cards_tree)


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
        self.cards_tree = None

    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        if self.cards_tree is None:
            if self.thread.isAlive():
                yield "Card database being built."
                return
            else:
                self.cards_tree = self.queue.pop()

        for c in identify_cards(e.contents, self.cards_tree):
            cardname = ''.join(c.get_phrase())
            yield link_element_template.format(link=base_url + '&quot '+ '+'.join(cardname.split(' ')) + '&quot', body=cardname)
