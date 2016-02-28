"""Checks for duplicates in the index numbers (which means content being
override and not used). The results will be saved into a text file.
The script doesn't take into account index numbers inside dev comments."""
import os, re, sys, argparse
from itertools import groupby
import common


def duplicate_checker(filepaths, encoding):
    log = ''
    for filepath in filepaths:
        lines = common.readlines(filepath, encoding)
        #gets the indices (expects a correct syntax, aside from spaces
        #at the beginning of the line)
        indices = [re.findall(r'^[ ]*\{([0-9]+)\}', l) for l in lines]
        indices = [int(i[0]) for i in indices if i]
        indices.sort()
        #groups indices and their count number; keeps duplicates only
        dupes = [(i, len(list(g))) for i, g in groupby(indices)]
        dupes = [(i, l) for (i, l) in dupes if l > 1]
        if dupes:
            log += filepath
            for dupe in dupes:
                log += "\n       This file has the "
                log += "index number {:d} repeated {:d} times!".format(*dupe)
            log += "\n\n"

    return log


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("target", help="Target folder")
    par.add_argument("-r", "--recursive", action="store_true",
                     help="Recursive folder search; the target path should \
                     contain the localization folders you want to check")
    args = par.parse_args()

    path = os.path.abspath(args.target)
    if not args.recursive:
        dirnames = [os.path.basename(path)]
    else:
        dirnames = common.listdirs(path)

    for dirname in dirnames:
        other_dirnames = [d for d in dirnames if d is not dirname]
        filepaths = common.pathfinder(path, excluded=other_dirnames)
        enc = common.encfinder(dirname)

        print("\n+ Working with {} ({})...".format(dirname, enc))
        log = duplicate_checker(filepaths, enc)

        if log:
            with open('dc-{}.txt'.format(dirname), 'w', encoding=enc) as flog:
                flog.write(log)
            print("  -> Duplicate lines were found!")
        else:
            print("  -> No duplicate lines found!")
