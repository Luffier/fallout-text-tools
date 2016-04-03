import os, re, sys, argparse
from itertools import combinations
from os.path import join, isdir, isfile, abspath, splitext, basename
from lang import Lang
from math import ceil
import common
try:
    from Levenshtein import ratio
except ImportError:
    import difflib
    def ratio(string1, string2):
        return difflib.SequenceMatcher(None, string1, string2).ratio()
    print("** python-Levenshtein module not found, using difflib instead **")
try:
    import ujson as json
except ImportError:
    import json
    print("** ujson module not found, using json instead **")

def similarity_finder(lang, thd=0.8):

    global_lang = lang.global_parser(complete=False)
    addresses = sorted(global_lang.items())

    sim = {}
    for address1, address2 in combinations(global_lang, 2):
        line_ratio = ratio(global_lang[address1], global_lang[address2])
        if line_ratio >= thd:
            line1, line2 = global_lang[address1], global_lang[address2]
            sim.setdefault(line1, {})
            sim[line1].setdefault(line2, line_ratio)
    return sim

#{ratio: [lines]}
def similarity_finder2(line, global_lang, thd=0.9):
    sim = {}
    for address in global_lang:
        line_ratio = ratio(global_lang[address], line)
        if line_ratio >= thd:
            line_ratio = ceil(line_ratio * 100)
            line2 = global_lang[address]
            sim.setdefault(line_ratio, [])
            sim[line_ratio].append(line2)
    return sim


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("target", help="Target localization folder", nargs='?')
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    target = Lang(abspath(args.target), args.clearcache)

    os.makedirs(Lang.cacheroot, exist_ok=True)
    cachepath = join(Lang.cacheroot, '{}-SIM.json'.format(target.dirname))

    if isfile(cachepath):
        print("Using cached global log ({}-SIM)".format(target.dirname))
        with open(cachepath, 'r', encoding=target.encoding) as cachein:
            sim = json.load(cachein)
    else:
        sim = similarity_finder(target)
        with open(cachepath, 'w', encoding=target.encoding) as cacheout:
            json.dump(sim, cacheout)
