"""Checks the syntax (open curly brackets and non numeric characters on the
index position) and saves a reference for any error found in a text file.
Any line break inside brackets or dev comments that don't start with the usual
number sign will raise a false positive (you can use lbr to minimaze false
positives. You'll have to fix any syntax error manually using the output text
as reference (it has both, the number line and the line itself). If you want
to check several folders, you can use the recursive mode"""
import os, re, sys, argparse
import common

#looks for lines with brackets (after discarding comments and empty lines),
#pairs them and flags if there's more than 3 pairs or a non-numeric character
#is found on the index section.
def syntax_checker(filepaths, encoding):
    log = ''
    #for skipping comments and empty lines
    unwanted_lines_p = re.compile(r'^[^\S\n]*(?:\#.*|)$')
    #for catching non-numeric characters inside the index position
    non_numeric_p = re.compile(r'[^\S\n]*\{.*([^\{\}0-9]+).*\}\{.*\}\{[^{]*\}')

    for filepath in filepaths:
        flag = False #for delimiting files in the log text
        lines = common.open2(filepath, encoding)
        lines = [(n, l) for (n, l) in enumerate(lines, start=1)]
        lines = [(n, l) for (n, l) in lines if not unwanted_lines_p.search(l)]

        for index, line in lines:
            brackets = [c for c in line if c in ('{', '}')]
            brackets = ''.join(brackets)
            bracket_pairs = brackets.count('{}')
            non_numeric = non_numeric_p.search(line)

            if not flag and ((bracket_pairs != 3) or non_numeric):
                flag = True
                log += filepath + "\n"

            if non_numeric:
                log += "{:<7d} Non-numeric on index   -->  ".format(index)
                log += "'{}'\n".format(line.replace('\n',''))
            if bracket_pairs < 3:
                log += "{:<7d} Less than three pairs  -->  ".format(index)
                log += "'{}'\n".format(line.replace('\n',''))
            elif bracket_pairs > 3:
                log += "{:<7d} More than three pairs  -->  ".format(index)
                log += "'{}'\n".format(line.replace('\n',''))

        if flag:
            log += "\n\n"

    return log


if __name__ == '__main__':

    help_msg = (146 * "*" +
    """\n Less tran 3 pairs of brackets: line break inside \
    brackets (false positive), dev comment without number sign (ugly) or \
    missing bracket/s (crash!)\n More than 3 pairs of brackets: inline dev \
    comment with brackets inside, 2 lines in one (not fatal but ugly) or a \
    'lost' set of brackets (crash!)\n Non-numeric character on index \
    setion: possibly a typo or a weird bracket configuration (crash!)\n""" +
    146 * "*" + "\n\n\n")

    par = argparse.ArgumentParser(description=syntax_checker.__doc__)
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
        filepaths = common.pathfinder(path, excluded=other_dirs)
        enc = common.encfinder(dirname)

        print("\n+ Working with {} ({})...".format(dirname, enc))
        log = syntax_checker(filepaths, enc)

        if log:
            log = help_msg + log
            with open('sc-{}.txt'.format(dirname), 'w', encoding=enc) as flog:
                flog.write(log)
            print("  -> One or more syntax errors were found!")
        else:
            print("  -> No syntax errors found!")
