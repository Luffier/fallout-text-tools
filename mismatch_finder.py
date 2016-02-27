"""For checking when two lines that are the same in the English files aren't in
the target language, helpfull for spoting inaccuracies and mantain a consistent
localization. The results use the JSON format (formatted for readability)."""
import os, re, sys, argparse
from math import factorial as fact
from itertools import combinations
import common, lazy_town
try:
    import ujson
except ImportError:
    import json
    print("* ujson module not found, using json instead *\n")

#checks when two lines that are the same in the English files aren't in the
#target language. It compares every line with the rest, across all files,
#meaning that with 42.116 lines (Fixt 0.81) there's a total of 886.857.670
#pairs (without repetitions) to compare, at 1.880.000 lines per second (avarage
#in my computer) it takes around 8 minutes.
def mismatch_finder(base, target):
    log = {"_stats_": []}
    base_alt = {}
    target_alt = {}
    #the indices in PIPBOY.MSG are dynamic (currently using this feature in the
    #SPANISH localization). It would raise a KeyError exception when it tries
    #to use those unique PIPBOY addresses in the Fixt dict.
    if target.get("PIPBOY.MSG") and base.get("PIPBOY.MSG"):
        for index in list(target["PIPBOY.MSG"]):
            if not base["PIPBOY.MSG"].get(index):
                target["PIPBOY.MSG"].pop(index)
    #transform the usual nested dict into a new dict with all the lines,
    #combining filename and index as the unique identifier of that line_eng
    #with the following structure: {"filename||index": "line_eng"}
    for afile in target:
        for index in target[afile]:
            target_alt[afile[:-4]+"||"+index] = target[afile][index]
    for afile in base:
        for index in base[afile]:
            base_alt[afile[:-4]+"||"+index] = base[afile][index]

    identifier_p = re.compile(r'^(.+)\|\|([0-9]+)$')

    #log structure: {"line_eng": {"line_loc": {"filename": [index]}}}
    mflags = 0
    for addr1, addr2 in combinations(target_alt, 2):
        if base_alt.get(addr1) == base_alt.get(addr2):
            line_eng = base_alt[addr1]
            if target_alt[addr1] != target_alt[addr2]:
                for addr in (addr1, addr2):
                    line_loc = target_alt[addr]
                    filename, index = identifier_p.search(addr).groups()
                    log.setdefault(line_eng, {})
                    log[line_eng].setdefault(line_loc, {})
                    log[line_eng][line_loc].setdefault(filename, [])
                    if index not in log[line_eng][line_loc][filename]:
                        log[line_eng][line_loc][filename].append(index)
                        mflags += 1

    total_pairs = fact(len(target_alt)) // (2*fact(len(target_alt) - 2))
    total_lines = len(target_alt)
    mlines = len(log) - 1
    log["_stats_"].append("Lines:   {}".format(total_lines))
    log["_stats_"].append("Pairs:   {}".format(total_pairs))
    log["_stats_"].append("Matches: {} (from {} lines)".format(mflags, mlines))

    return log


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("base", help="ENGLISH text folder")
    par.add_argument("target", help="Target localization folder")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    target_enc = common.encfinder(args.target)
    base_enc = common.encfinder(args.base)

    target_dict = lazy_town.analyzer(args.target, target_enc, args.clearcache)
    base_dict = lazy_town.analyzer(args.base, base_enc, args.clearcache)

    cachepath = os.path.join('.', 'ftt-cache')
    os.makedirs(cachepath, exist_ok=True)
    dirnames = [os.path.basename(d) for d in (args.base, args.target)]
    cachepath = os.path.join(cachepath, '{}@@{}.json'.format(*dirnames))

    if os.path.isfile(cachepath) and not args.clearcache:
        print("Using cached global log ({}@@{})".format(*dirnames))
        with open(cachepath, 'r', encoding=target_enc) as cachein:
            try:
                log = ujson.load(cachein)
            except NameError:
                log = json.load(cachein)
    else:
        print("\nWORKING...")
        log = mismatch_finder(base_dict, target_dict)
        with open(cachepath, 'w', encoding=target_enc) as cacheout:
            try:
                ujson.dump(log, cacheout)
            except NameError:
                json.dump(log, cacheout)

    for comment in log["_stats_"]:
        print(comment)

    #log formatting for readability
    log.pop("_stats_")
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
              'w', encoding=target_enc) as flog:
        try:
            ujson.dump(log, flog, ensure_ascii=False, indent=4, sort_keys=True)
        except NameError:
            json.dump(log, flog, ensure_ascii=False, indent=4, sort_keys=True)
