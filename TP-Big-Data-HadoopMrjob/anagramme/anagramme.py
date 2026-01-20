#!/usr/bin/env python3

import re
import unicodedata

from mrjob.job import MRJob
from mrjob.protocol import RawValueProtocol


WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
VOWELS = set("aeiouy")


def normalize_word(word):
    letters = []
    for ch in word.lower():
        if not ch.isalpha():
            continue
        decomp = unicodedata.normalize("NFD", ch)
        base = decomp[0]
        if base in VOWELS:
            letters.append(base)
        else:
            letters.append(ch)
    return "".join(letters)


def signature(word):
    normalized = normalize_word(word)
    if not normalized:
        return ""
    return "".join(sorted(normalized))


class MRAnagrammes(MRJob):
    OUTPUT_PROTOCOL = RawValueProtocol

    def mapper(self, _, line):
        for word in WORD_RE.findall(line):
            word_lc = word.lower()
            sig = signature(word_lc)
            if sig:
                yield sig, word_lc

    def reducer(self, sig, words):
        unique = sorted(set(words))
        if len(unique) >= 2:
            yield sig, ", ".join(unique)


if __name__ == "__main__":
    MRAnagrammes.run()
