import os, re, sys, shutil, itertools
from math import factorial


try:
    import Levenshtein
    isLevenshtein = True
except ImportError:
    import difflib
    isLevenshtein = False

from common import *
from lazy_town import analyzer


#logs similar lines in a given dic; not very usuful as of now
def similarity_finder(dic, threshold = (1, 0.9)):

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
    print("\n\nThere were %i lines above the threshold and %i below." % (above_threshold, below_threshold))

    return output_text

#if two lines are the same in the English files (base) then checks if those same
#lines aren't in the target localization
def mismatch_finder(base, target):

    output_text = ''

    flag = False
    count_total = len(base.keys())

    for afile in target.keys():
        for index1, index2 in itertools.combinations(target[afile], 2):
            if base[afile].get(index1) == base[afile].get(index2):
                if target[afile].get(index1) != target[afile].get(index2):
                    if not flag:
                        output_text += "\n\n%s\n\n" % afile
                    flag = True
                    output_text += "\n    %s --> '%s'\n    %s --> '%s'\n" % (index1, target[afile].get(index1), index2, target[afile].get(index2))
        flag = False
    return output_text



#similar to mismatch_finder but on a global scale (expect it to be very slow)
#it compares every line with the rest, across all files, meaning that with 42.116
#lines (Fixt 0.81) there's a total of 886.857.670 of pairs (without repetitions)
#to compare, at 1.880.000 lines per second (avarage in my computer) it would take
#around 8 minutes
def mismatch_finder_global(base, target):

    output_text = ''

    base_alt = {}
    target_alt = {}

    for afile in target.keys():
        for index in target[afile].keys():
            target_alt[afile+index] = target[afile][index]

    for afile in base.keys():
        for index in base[afile].keys():
            base_alt[afile+index] = base[afile][index]

    flag = False
    count_total = factorial( len(base_alt.keys()) ) // (2 *  factorial( len(base_alt.keys()) - 2))
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
                output_text += "\n    %s --> '%s'\n    %s --> '%s'\n" % (index1, target_alt.get(address1), index2, target_alt.get(address2))
        flag = False
    return output_text


if __name__ == '__main__':

    option = int(input("Option 1, 2 or 3?: "))

    if option == 1:
        base = 'ENGLISH_FIXT'
        if not os.path.isdir(base):
            input("\n%s folder missing. Aborting..." % base)
            exit()

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


    elif option == 2:
        base = 'ENGLISH_FIXT'
        if not os.path.isdir(base):
            input("\n%s folder missing. Aborting..." % base)
            exit()

        dirnames = listdirs(excluded = [base])
        for i in range(len(dirnames)):
            print("%i) %s" % (i, dirnames[i]))

        target = dirnames[int(input("\nType the number of the language/folder to work with: "))]


        target_enc = encfinder(target)
        base_enc = encfinder(base)

        target_dic = analyzer(target, target_enc)
        base_dic = analyzer(base, base_enc)

        result = mismatch_finder_global(base_dic, target_dic)
        with open('mfG_result.txt', 'w', encoding = target_enc) as fileout:
            fileout.write(result)

    elif option == 3:

        dirnames = listdirs()
        for i in range(len(dirnames)):
            print("%i) %s" % (i, dirnames[i]))
        target = dirnames[int(input("\nType the number of the language/folder to work with: "))]

        target_enc = encfinder(target)
        target_dic = analyzer(target, target_enc)

        result = similarity_finder(target_dic)
        with open('sf_result.txt', 'w', encoding = target_enc) as fileout:
            fileout.write(result)
