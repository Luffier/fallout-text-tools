"""Checks for duplicates in the index numbers (which means content being
override and not used). The results will be saved into a text file.
The script doesn't take into account index numbers inside dev comments."""
import os, re, sys, argparse
import common


def duplicate_checker(files, enc):

    log = ''
    for afile in files:

        lines = common.open2(afile, encoding=enc)
        #remove dev comments and others
        lines = [l for l in lines if not l.startswith('#')]
        lines = [l for l in lines if l.startswith('{')]

        indices = [re.findall(r'^[ ]*\{([0-9]+)\}', l)[0] for l in lines]
        indices = [int(i) for i in indices]

        #fills matches if there's any duplicate and records it
        matches = [i for i in indices if indices.count(i) > 1]
        if matches:
            log += afile
            matches.sort()
            while matches:
                log += "\n       This file has the "
                log += "index number {:d} ".format(matches[0])
                log += "repeated {:d} times!".format(matches.count(matches[0]))
                matches[:] = [m for m in matches if m != matches[0]]
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
        other_dirs = [d for d in dirnames if d is not dirname]
        thefiles = common.pathfinder(path, excluded=other_dirs)
        enc = common.encfinder(dirname)

        print("\n+ Working with {} ({})...".format(dirname, enc))
        log = duplicate_checker(thefiles, enc)

        if log:
            with open('dc-{}.txt'.format(dirname), 'w', encoding=enc) as flog:
                flog.write(log)
            print("  -> Duplicate lines were found!")
        else:
            print("  -> No duplicate lines found!")
