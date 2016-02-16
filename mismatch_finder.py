"""For checking when two lines that are the same in the English files aren't in
the target language, helpfull for spoting inaccuracies and mantain a consistent
localization. Normal mode does this in a file basis, global compares every line
with the rest across all files (very slow)."""
import os, re, sys, argparse, itertools
from math import factorial
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

    output_text = ''

    flag = False
    count_total = len(base)

    for afile in target:
        for index1, index2 in itertools.combinations(target[afile], 2):
            if base[afile].get(index1) == base[afile].get(index2):
                if target[afile].get(index1) != target[afile].get(index2):
                    if not flag:
                        output_text += "\n\n%s{\n" % afile
                    flag = True
                    output_text += "\n%8s --> '%s'" % (index1, target[afile].get(index1))
                    output_text += "\n%8s --> '%s'" % (index2, target[afile].get(index2))
                    output_text += "\n      EN --> '%s'\n" % (base[afile].get(index1))
        if flag:
            output_text += "\n}"
        flag = False
    return output_text


#similar to mismatch_finder but on a global scale (expect it to be very slow)
#it compares every line with the rest, across all files, meaning that with
#42.116 lines (Fixt 0.81) there's a total of 886.857.670 pairs (w/o repetitions)
#to compare, at 1.880.000 lines per second (avarage in my computer) it would
#take around 8 minutes.
def mismatch_finder_global(base, target):

    output_text = ''

    base_alt = {}
    target_alt = {}

    for afile in target:
        for index in target[afile]:
            target_alt[afile+index] = target[afile][index]

    for afile in base:
        for index in base[afile]:
            base_alt[afile+index] = base[afile][index]

    flag = False
    count_total = factorial(len(base_alt)) // (2 *  factorial(len(base_alt) - 2))
    fname_pattern = re.compile(r'[0-9]{3,5}')
    index_pattern = re.compile(r'.*\.MSG', re.I)
    print("\nTotal pairs: %s\n" % count_total)

    for address1, address2 in itertools.combinations(target_alt, 2):
        if base_alt.get(address1) == base_alt.get(address2):
            if target_alt.get(address1) != target_alt.get(address2):
                if not flag:
                    filename1 = fname_pattern.sub('', address1)
                    filename2 = fname_pattern.sub('', address2)
                    output_text += "\n\n%s / %s\n\n" % (filename1, filename2)
                flag = True
                index1 = index_pattern.sub('', address1)
                index2 = index_pattern.sub('', address2)
                output_text += "\n %7s --> '%s'\n" % (index1, target_alt.get(address1))
                output_text += "\n %7s --> '%s'\n" % (index2, target_alt.get(address2))
                output_text += "\n      EN --> '%s'\n" % (base_alt.get(address1))
        flag = False

    return output_text


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
        result = mismatch_finder(base_dict, target_dict)
        with open('mf_result.txt', 'w', encoding=target_enc) as foutput:
            foutput.write(result)

    if args.globalmode:
        result = mismatch_finder_global(base_dict, target_dict)
        with open('mfG_result.txt', 'w', encoding=target_enc) as foutput:
            foutput.write(result)
