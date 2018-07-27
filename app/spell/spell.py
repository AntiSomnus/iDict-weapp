import re
from collections import Counter

from .. import conn


class SpellCorrector(object):
    def __init__(self):
        sql = ('SELECT word, base FROM word_mini')
        data = conn.execute(sql).fetchall()
        self.data = {item[0]: item[1] for item in data}

    def correction(self, word):
        candidates = self.candidates(word)
        if candidates:
            return min(candidates, key=self.data.get)
        else:
            return word

    def candidates(self, word):
        return {**self.known([word]),
                **self.known(self.edits1(word)),
                **self.known(self.edits2(word))}

    def known(self, words):
        return {w: self.data[w] for w in words if w in self.data.keys()}

    def edits1(self, word):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))
