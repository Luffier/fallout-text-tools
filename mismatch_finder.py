import os, re, sys, shutil, itertools

try:
    import Levenshtein
    isLevenshtein = True
except ImportError:
    import difflib
    isLevenshtein = False

from main import *
from lazy_town import analyzer


#logs similar lines in a given dic; not very usuful as of now
def same_file_comparator(dic, threshold = (1, 0.9):

    above_threshold = 0
    below_threshold = 0

    output_text = ''

    if isLevenshtein:
        ratio = lambda x, y: Levenshtein.ratio(x, y)
    else:
        ratio = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()

    flag = False
    count = 0
    count_total = len(dic.keys())
    for afile in dic.keys():
        for index1, index2 in itertools.combinations(dic[afile], 2):
            if threshold[0] > ratio( dic[afile].get(index1), dic[afile].get(index2) ) >= threshold[1]:
                if not flag: output_text += "\n\n%s\n\n" % afile
                flag = True
                above_threshold += 1
                output_text += "    %s --> %s\n    %s --> %s" % (index1, dic[afile].get(index1), index2, dic[afile].get(index2))
            else:
                below_threshold += 1
        flag = False
        count += 1
        sys.stdout.write("\r%s/%s" % (count, count_total))
        sys.stdout.flush()
    print("There were %i lines above the threshold and %i below." % (above_threshold, below_threshold))

    return output_text

#if two lines are the same in the English files (base) then checks if those same
#lines aren't in the target localization
def mismatch_finder(base, target):

    output_text = ''

    flag = False
    count = 0
    count_total = len(base.keys())

    for afile in target.keys():
        for index1, index2 in itertools.combinations(target[afile], 2):
            if base[afile].get(index1) == base[afile].get(index2):
                if target[afile].get(index1) != target[afile].get(index2):
                    if not flag:
                        output_text += "\n\n%s\n\n" % afile
                    flag = True
                    output_text += "\n    %s --> '%s'\n    %s --> '%s'\n" % (index1, target[afile].get(index1), index2, target[afile].get(index2))
        count += 1
        sys.stdout.write("\r%s/%s" % (count, count_total))
        sys.stdout.flush()
        flag = False
    return output_text


if __name__ == '__main__':

    base = 'ENGLISH_FIXT'
    if not os.path.isdir(base):
        input("\n%s folder missing. Aborting..." % base)
        exit()
    target = 'SPANISH_MALE'

    dirnames = listdirs(excluded = [base])
    for i in range(len(dirnames)):
        print("%i) %s" % (i, dirnames[i]))

    target = dirnames[int(input("\nType the number of the language/folder to work with: "))]


    target_enc = encfinder(target)
    base_enc = encfinder(base)

    target_dic = analyzer(target, target_enc)
    base_dic = analyzer(base, base_enc)

    result = mismatch_finder(base_dic, target_dic)
    with open('mf_result.txt', 'w', encoding = target_enc) as fileout:
        fileout.write(result)
