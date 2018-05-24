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
card_pattern = re.compile(r'\[\[[^\[^\].]*\]\]')
link_element_template = '<a target="_blank" href="{link}">{body}</a>'
base_url = 'https://scryfall.com/search?q='


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


class SuffixTree:

    def __init__(self, list_of_phrases):
        self.root = Node(None)
        for p in list_of_phrases:
            self.search(p, insert=True)

    def search(self, list_of_words, insert=False, key=None):
        words_iter = iter(list_of_words)
        cur_token = next(words_iter)
        cur_node = self.root
        while True:
            # guard
            if len(cur_node.children) == 0 and not insert:
                return (cur_node, list(words_iter))
            # check children for match
            for n in cur_node.children:
                if n.value == cur_token:
                    cur_node = n
                    try:
                        cur_token = next(words_iter)
                    except StopIteration:
                        return (cur_node, list(words_iter))
                    break
            else:
                # no matching chilrden
                if not insert:
                    return (cur_node, [cur_token] + list(words_iter))
                # make new node
                new_node = Node(cur_token)
                cur_node.add_child(new_node)
                cur_node = new_node
                try:
                    cur_token = next(words_iter)
                except StopIteration:
                    return (cur_node, list(words_iter))

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


def download_cards_to_file(destination='resources/cards.json'):
    resp = requests.get(url, stream=True)
    myfile = io.BytesIO(resp.content)
    with zipfile.ZipFile(myfile) as myzip:
        with myzip.open('AllCards.json') as cardsfile:
            cards = json.load(cardsfile)
    with open(destination, 'w') as f:
        f.write(json.dumps(cards))



def fetch(mailbox, target):
    download_cards_to_file(target)
    with open(target) as f:
        cards = json.load(f)
    cards_tree = SuffixTree(list(name.strip()) for name in cards)
    mailbox.append(cards_tree)


def identify_cards(s, cards_tree):
    tokens = []
    for c in s:
        tokens.append(c)
        found_cards = list(cards_tree.find_all(tokens))
        if len(found_cards) == 0:
            tokens = [c]
        elif len(found_cards) == 1:
            card = found_cards.pop()
            p = card.get_phrase()
            if len(p) == len(tokens):
                yield card



class Plugin(parsing.Plugin):
    """An example plugin that simply splits the entry on spaces."""
    name = 'Magic: the Gathering Fetcher'
    def __init__(self):
        super().__init__()
        self.queue = []
        self.cards_file_path = os.path.join(self.resources_path,'cards.json')
        self.thread = threading.Thread(target=fetch, kwargs=dict(mailbox=self.queue, target=self.cards_file_path))
        self.thread.start()
        self.cards_tree = None

    def parse_entry(self, e: models.JournalEntry) -> 'iterable[str]':
        if self.cards_tree is None:
            if not self.thread.isAlive() :
                self.cards_tree = self.queue.pop()
            yield "Card database still downloading."
        else:
            for c in identify_cards(e.contents, self.cards_tree):
                cardname = ''.join(c.get_phrase())
                yield link_element_template.format(link=base_url + '+'.join(cardname.split(' ')), body=cardname)
        return
        seen = set()
        cards = list(card_pattern.findall(e.contents))
        for card in cards:
            if card not in seen:
                seen.add(card)
                cardname = card[2:-2]
                yield link_element_template.format(link=base_url + '+'.join(cardname.split(' ')), body=cardname)
