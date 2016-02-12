import os, re, sys, argparse, itertools
from math import factorial


try:
    import Levenshtein
    isLevenshtein = True
except ImportError:
    import difflib
    isLevenshtein = False

from common import *
from lazy_town import analyzer


#logs similar lines within a loc_dict (analyzer); not very usuful as of now
def similarity_finder(loc_dict, threshold = (1, 0.9)):

    above_threshold = 0
    below_threshold = 0

    output_text = ''

    if isLevenshtein:
        ratio = lambda x, y: Levenshtein.ratio(x, y)
    else:
        ratio = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()

    flag = False
    count = 0
    count_total = len(loc_dict.keys())
    for afile in loc_dict.keys():
        for index1, index2 in itertools.combinations(loc_dict[afile], 2):
            if threshold[0] > ratio( loc_dict[afile].get(index1), loc_dict[afile].get(index2) ) >= threshold[1]:
                if not flag: output_text += "\n\n%s\n\n" % afile
                flag = True
                above_threshold += 1
                output_text += "    %s --> %s\n    %s --> %s" % (index1, loc_dict[afile].get(index1), index2, loc_dict[afile].get(index2))
            else:
                below_threshold += 1
        flag = False
        count += 1
        sys.stdout.write("\r%s/%s" % (count, count_total))
        sys.stdout.flush()
    print("\n\nThere were %i lines above the threshold and %i below." % (above_threshold, below_threshold))
    return output_text


if __name__ == '__main__':

    par = argparse.ArgumentParser()
    par.add_argument("target", help="Target localization folder", nargs='?')
    par.add_argument("-s", "--similmode", action="store_true", help="Similarity mode")
    par.add_argument("-c", "--clearcache", action="store_true", help="Clears json cache files")
    args = par.parse_args()

    if args.similmode:
        target_enc = encfinder(args.target)
        target_dic = analyzer(args.target, target_enc)

        result = similarity_finder(target_dic)
        with open('sf_result.txt', 'w', encoding = target_enc) as fileout:
            fileout.write(result)
