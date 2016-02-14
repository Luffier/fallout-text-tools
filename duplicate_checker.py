import os, re, sys, argparse

from common import *


def duplicate_checker(files, enc):

    result = ''

    for afile in files:

        opt = [enc, None] #opt = [enconding, errors]
        lines = alt_read(afile, opt)

        #remove dev comments and others
        lines = [line for line in lines if not line.startswith('#')]
        lines = [line for line in lines if line.startswith('{')]

        indices = [re.findall(r'^[ ]*\{([0-9]+)\}', line)[0] for line in lines]
        indices = [int(index) for index in indices]

        #fills matches if there's any duplicate and records it
        matches = [index for index in indices if indices.count(index) > 1]
        if matches:
            result = result + afile
            matches.sort()
            while matches:
                result = result + "\n       This file has the index number %s repeated %s times!" % (str(matches[0]), str(matches.count(matches[0])))
                matches[:] = [match for match in matches if match != matches[0]]
            result = result + "\n\n"

    return result


if __name__ == '__main__':

    par = argparse.ArgumentParser(description="Checks for duplicates in the \
    index numbers (which means content being override and unused). The result \
    will be saved into 'dc-result.txt'. The script doesn't take into account \
    index numbers inside dev comments.")
    par.add_argument("target", help="Target folder")
    par.add_argument("-r", "--recursive", action="store_true",
                      help="Recursive folder search; the target path should \
                      contain the localization folders you want to check")
    args = par.parse_args()


    path = os.path.abspath(args.target)
    if not args.recursive:
        dirnames = [os.path.basename(path)]
    else:
        dirnames = listdirs(path)

    for dirname in dirnames:
        other_dirs = [d for d in dirnames if d is not dirname]
        thefiles = pathfinder(path, excluded = ['__pycache__'] + other_dirs)
        enc = encfinder(dirname)

        print("\n+ Working with %s (%s)..." % (dirname, enc))
        output = duplicate_checker(thefiles, enc)

        if output:
            with open('dc-result-%s.txt' % dirname, 'w', encoding=enc) as foutput:
                foutput.write(output)
            print("  -> Duplicate lines were found!")
        else:
            print("  -> No duplicate lines found!")
