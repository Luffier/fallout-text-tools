import os, re, sys, argparse, itertools
from math import factorial
import common
from lazy_town import analyzer
try:
    import Levenshtein
    ratio = lambda x, y: Levenshtein.ratio(x, y)
except ImportError:
    import difflib
    lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
    print("python-Levenshtein module not found, using difflib instead")


#logs similar lines within a loc dict (analyzer); not very usuful as of now
def similarity_finder(loc, thd=0.9):

    log = ''
    above_thd = 0
    below_thd = 0

    flag = False

    total_count = len(loc)
    for count, afile in enumerate(loc, start=1):
        for index1, index2 in itertools.combinations(loc[afile], 2):
            if ratio(loc[afile].get(index1), loc[afile].get(index2)) >= thd:
                if not flag:
                    log += "\n\n{}\n\n".format(afile)
                flag = True
                above_thd += 1
                log += "{:>8} --> {}\n".format(index1, loc[afile].get(index1))
                log += "{:>8} --> {}".format(index2, loc[afile].get(index2))
            else:
                below_thd += 1
        flag = False
        sys.stdout.write("\r{}/{}".format(count, total_count))
        sys.stdout.flush()
    print("Lines above the threshold: {:d}".format(above_thd))
    print("Lines below the threshold: {:d}".format(below_thd))

    return log[2:]


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("target", help="Target localization folder", nargs='?')
    par.add_argument("-s", "--similmode", action="store_true",
                     help="Similarity mode")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    if args.similmode:
        target_enc = common.encfinder(args.target)
        target_dic = analyzer(args.target, target_enc)

        log = similarity_finder(target_dic)
        with open('sf_result.txt', 'w', encoding=target_enc) as flog:
            flog.write(result)
