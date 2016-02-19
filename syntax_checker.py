"""Checks the syntax (open curly brackets and non numeric characters on the
index position) and saves a reference for any error found in a text file.
Any line break inside brackets or dev comments that don't start with the usual
number sign will raise a false positive (you can use lbr to minimaze false
positives. You'll have to fix any syntax error manually using the output text
as reference. There are two modes, normal and full. Full mode adds the line
number to any flag encountered, but unfortunately it also makes the script
slower. If you want to check several folders, you can use the recursive mode"""
import os, re, sys, fnmatch, argparse
import common

#looks for lines with brackets (after discarding comments and empty lines),
#pairs them and flags if there's more than 3 pairs or a non-numeric character
#is found on the index section.
def syntax_checker(files, enc, fullmode=False):
    log = ''
    for afile in files:
        flag = False

        lines = common.open2(afile, encoding=enc)

        if fullmode:
            reference = lines

        lines = [l for l in lines if not re.findall(r'^[ ]*#', l)]
        lines = [l for l in lines if l != '\n']
        lines = [l for l in lines if not re.findall(r'^[ ]+$', l)]
        lines = [l for l in lines if l]

        for line in lines:

            brackets = [char for char in line if char in ('{', '}')]
            brackets = ''.join(brackets)
            npairs = brackets.count('{}')

            match = re.findall(r'[ ]*\{.*([^\{\}0-9]+).*\}'
                               r'\{.*\}'
                               r'\{[^{]*\}', line)

            if ((npairs != 3) and (not flag)) or match:
                flag = True
                log += afile + "\n"

            if match:
                if fullmode:
                    log += "{:d}".format(reference.index(line) + 1)
                log += "        Non-numeric on index   -->  "
                log += "'{}'\n".format(line.replace('\n', ''))
            if npairs < 3:
                if fullmode:
                    log += "{:d}".format(reference.index(line) + 1)
                log += "        Less than three pairs  -->  "
                log += "'{}'\n".format(line.replace('\n', ''))
            elif npairs > 3:
                if fullmode:
                    log += "{:d}".format(reference.index(line) + 1)
                log += "        More than three pairs  -->  "
                log += "'{}'\n".format(line.replace('\n', ''))

        if flag:
            log += "\n\n"
        flag = False

    return log


if __name__ == '__main__':

    help_msg = (146*"*" +
    "\n Less tran 3 pairs of brackets: line break inside " +
    "brackets (false positive), dev comment without number sign (ugly) or " +
    "missing bracket/s (crash!)\n More than 3 pairs of brackets: inline dev " +
    "comment with brackets inside, 2 lines in one (not fatal but ugly) or a " +
    "'lost' set of brackets (crash!)\n Non-numeric character on index " +
    "setion: possibly a typo or a weird bracket configuration (crash!)\n" +
    146*"*" + "\n\n\n")

    par = argparse.ArgumentParser(description=syntax_checker.__doc__)
    par.add_argument("target", help="Target folder")
    par.add_argument("-f", "--fullmode", action="store_true", help="Full mode")
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
        log = syntax_checker(thefiles, enc, fullmode=args.fullmode)

        if log:
            log = help_msg + log
            with open('sc-{}.txt'.format(dirname), 'w', encoding=enc) as flog:
                flog.write(log)
            print("  -> One or more syntax errors were found!")
        else:
            print("  -> No syntax errors found!")
