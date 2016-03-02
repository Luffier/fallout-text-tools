"""For checking when two lines that are the same in the English files aren't in
the target language, helpfull for spoting inaccuracies and mantain a consistent
localization. The results use the JSON format (formatted for readability)."""
import os, sys, argparse
from math import factorial as fact
from itertools import combinations
from os.path import join, isfile, abspath
import common
from lang import Lang
try:
    import ujson as json
except ImportError:
    import json
    print("** ujson module not found, using json instead **\n")


#checks when two lines that are the same in the English files aren't in the
#target language. It compares every line with the rest, across all files.
#With 42.116 lines (Fixt 0.81) there's a total of 886.857.670 pairs (without
#repetitions) to compare.
def mismatch_finder(base, target):

    #the indices in PIPBOY.MSG are dynamic (currently using this feature in the
    #SPANISH localization). It would raise a KeyError exception when it tries
    #to use those unique PIPBOY addresses in the Fixt dict.
    target.purge_with(base)
    target.purge_with(base, limiter=['pipboy'])

    base_global = base.global_parser()
    target_global = target.global_parser()

    #log structure: {"line_eng": {"line_loc": {"filename": [index]}}}
    log = {}
    flags = 0
    for address1, address2 in combinations(target_global, 2):
        if base_global.get(address1) == base_global.get(address2):
            if target_global[address1] != target_global[address2]:
                line_eng = base_global[address1]
                for address in (address1, address2):
                    line_loc = target_global[address]
                    filename, index = Lang.id_pattern.search(address).groups()
                    log.setdefault(line_eng, {})
                    log[line_eng].setdefault(line_loc, {})
                    log[line_eng][line_loc].setdefault(filename, [])
                    if index not in log[line_eng][line_loc][filename]:
                        log[line_eng][line_loc][filename].append(index)
                        flags += 1

    line_count = len(target_global)
    log["_flags_"] = flags
    log["_pairs_"] = fact(line_count) // (2*fact(line_count-2))
    log["_lines_"] = line_count

    return log


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("base", help="ENGLISH text files")
    par.add_argument("target", help="Target localization files")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    par.add_argument("-v", "--verbosity", action="store_true",
                     help="Nifty stats")
    args = par.parse_args()

    base = Lang(abspath(args.base), args.clearcache)
    target = Lang(abspath(args.target), args.clearcache)

    os.makedirs(Lang.cacheroot, exist_ok=True)
    dirnames = (base.dirname, target.dirname)
    cachepath = join(Lang.cacheroot, '{}@@{}.json'.format(*dirnames))

    if isfile(cachepath) and not args.clearcache:
        print("Using cached global log ({}@@{})".format(*dirnames))
        with open(cachepath, 'r', encoding=target.encoding) as cachein:
            log = json.load(cachein)
    else:
        print("\nWORKING...")
        log = mismatch_finder(base, target)
        with open(cachepath, 'w', encoding=target.encoding) as cacheout:
            json.dump(log, cacheout)

    if args.verbosity:
        print("Total lines:   {}".format(log["_lines_"]))
        print("Total pairs:   {}".format(log["_pairs_"]))
        print("Matches: {} (from {} lines)".format(log["_flags_"], len(log)-1))

    #log formatting for readability
    for stat in ('_flags_', '_lines', '_pairs_'):
        log.pop(stat, None)
    for line_eng in log:
        width_max = max(map(len, log[line_eng].keys()))
        lines_fmt = []
        for line_loc in list(log[line_eng]):
            line_fmt = ""
            line_fmt += "{}".format(line_loc.replace('\n',''))
            width = width_max - len(line_loc) + 4
            for filename in log[line_eng][line_loc]:
                line_fmt += width * " " + "{}".format(filename)
                for index in log[line_eng][line_loc][filename]:
                    line_fmt += " {}".format(index)
            log[line_eng].pop(line_loc)
            lines_fmt.append(line_fmt)
        log[line_eng] = lines_fmt

    with open('mf-{}.json'.format(args.target),
              'w', encoding=target.encoding) as flog:
        try:
            json.dump(log, flog, ensure_ascii=False, indent=4, sort_keys=True)
        except NameError:
            json.dump(log, flog, ensure_ascii=False, indent=4, sort_keys=True)
