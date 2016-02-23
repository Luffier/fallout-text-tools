"""For checking when two lines that are the same in the English files aren't in
the target language, helpfull for spoting inaccuracies and mantain a consistent
localization. Normal mode does this in a file basis, global compares every line
with the rest across all files (very slow)."""
import os, re, sys, argparse
from math import factorial as fact
from itertools import combinations
import common, lazy_town
try:
    import Levenshtein
    ratio = lambda x, y: Levenshtein.ratio(x, y)
except ImportError:
    import difflib
    ratio = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
    print("python-Levenshtein module not found, using difflib instead")


#checks when two lines that are the same in the base language aren't in the
#target, this is done in a file basis
def mismatch_finder(base, target):
    log = ''
    for afile in target:
        flag = False #for delimiting files in the log text
        for index1, index2 in combinations(target[afile], 2):
            if base[afile].get(index1) == base[afile].get(index2):
                if target[afile][index1] != target[afile][index2]:
                    if not flag:
                        log += "\n\n{}{\n".format(afile)
                        flag = True
                    log += "\n{:>8} --> ".format(index1)
                    log += "'{}'".format(target[afile].get(index1))
                    log += "\n{:>8} --> ".format(index2)
                    log += "'{}'".format(target[afile].get(index2))
                    log += "\n{:>8} --> ".format("EN")
                    log += "'{}'\n".format(base[afile].get(index1))
        if flag:
            log += "\n}"
    return log


#similar to mismatch_finder but on a global scale (expect it to be very slow)
#it compares every line with the rest, across all files, meaning that with
#42.116 lines (Fixt 0.81) there's a total of 886.857.670 pairs (no repetitions)
#to compare, at 1.880.000 lines per second (avarage in my computer) it would
#take around 8 minutes.
def mismatch_finder_global(base, target):
    log = ''
    base_alt = {}
    target_alt = {}
    #the indices in PIPBOY.MSG are dynamic (currently using this feature in the
    #SPANISH localization). It would raise a KeyError exception when it tries
    #to use those unique PIPBOY addresses in the Fixt dict.
    for index in list(target["PIPBOY.MSG"]):
        if not base["PIPBOY.MSG"].get(index):
            target["PIPBOY.MSG"].pop(index)
    #transform the usual nested dict into a new dict with all the lines,
    #combining filename and index as the unique identifier of that line with
    #the following structure: {"filename||index":"line"}
    for afile in target:
        for index in target[afile]:
            target_alt[afile[:-4]+"||"+index] = target[afile][index]
    for afile in base:
        for index in base[afile]:
            base_alt[afile[:-4]+"||"+index] = base[afile][index]


    identifier_p = re.compile(r'^(.+)\|\|([0-9]+)$')
    total_pairs = fact(len(target_alt)) // (2*fact(len(target_alt) - 2))
    print("\nTotal pairs: {:d}\n".format(total_pairs))

    for address1, address2 in combinations(target_alt, 2):
        if base_alt.get(address1) == base_alt.get(address2):
            if target_alt[address1] != target_alt[address2]:
                filename1, index1 = identifier_p.search(address1).groups()
                filename2, index2 = identifier_p.search(address2).groups()
                log += "{:>12.12}".format(filename1)
                log += "{:>7}  ".format(index1)
                log += "'{}'\n".format(target_alt[address1].replace("\n", ''))
                log += "{:>12.12}".format(filename2)
                log += "{:>7}  ".format(index2)
                log += "'{}'\n".format(target_alt[address2].replace("\n", ''))
                log += "{:>19}  ".format("EN")
                log += "'{}'\n\n".format(base_alt[address1].replace("\n", ''))

    return log


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("base", help="Base localization folder (ENGLISH)")
    par.add_argument("target", help="Target localization folder")
    par.add_argument("-n", "--normalmode", action="store_true",
                     help="Normal mode")
    par.add_argument("-g", "--globalmode", action="store_true",
                     help="Global mode")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    target_enc = common.encfinder(args.target)
    base_enc = common.encfinder(args.base)

    target_dict = lazy_town.analyzer(args.target, target_enc, args.clearcache)
    base_dict = lazy_town.analyzer(args.base, base_enc, args.clearcache)

    if args.normalmode:
        log = mismatch_finder(base_dict, target_dict)
        log_filename = 'mf-{}.txt'.format(args.target)
        with open(log_filename, 'w', encoding=target_enc) as flog:
            flog.write(log)

    if args.globalmode:
        log = mismatch_finder_global(base_dict, target_dict)
        log_filename = 'mfG-{}.txt'.format(args.target)
        with open(log_filename, 'w', encoding=target_enc) as flog:
            flog.write(log)
