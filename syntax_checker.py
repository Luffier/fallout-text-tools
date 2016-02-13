import os, re, fnmatch, argparse

from common import *


#looks for lines with brackets (after discarding comments and empty lines),
#pairs them and flags if there's more than 3 pairs or a non-numeric character
#is found on the index section.
def syntax_checker(files, enc, fullmode=False):

    result = ''

    for afile in files:
        flag = False

        par = [enc, None] #parameters = [enconding, errors]
        lines = alt_read(afile, par)

        if fullmode: reference = lines

        lines = [line for line in lines if not re.findall(r'^[ ]*#', line)]
        lines = [line for line in lines if line != '\n']
        lines = [line for line in lines if not re.findall(r'^[ ]+$', line)]
        lines = [line for line in lines if line]

        for line in lines:

            brackets = [char for char in line if char in ('{','}')]
            brackets = ''.join(brackets)
            npairs = brackets.count('{}')

            match = re.findall(r'[ ]*\{.*([^\{\}0-9]+).*\}\{.*\}\{[^{]*\}', line)

            if ((npairs != 3) and (not flag)) or match:
                flag = True
                result += afile + "\n"

            if match:
                if fullmode: result += "%4s" % str(reference.index(line) + 1)
                result += "        Non-numeric on index  -->  '%s'\n" % line.replace('\n','')

            if npairs < 3:
                if fullmode: result += "%4s" % str(reference.index(line) + 1)
                result += "        Less tran three pairs -->  '%s'\n" % line.replace('\n','')

            elif npairs > 3:
                if fullmode: result += "%4s" % str(reference.index(line) + 1)
                result += "        More than three pairs -->  '%s'\n" % line.replace('\n','')

        if flag: result += "\n\n"
        flag = False

    return result


if __name__ == '__main__':


    help_msg = (146*"*" + "\n Less tran 3 pairs of brackets: line break inside "
    "brackets (false positive), dev comment without number sign (ugly) or missing "
    "bracket/s (crash!)\n More than 3 pairs of brackets: inline dev comment with "
    "brackets inside, 2 lines in one (not fatal but ugly) or a 'lost' set of "
    "brackets (crash!)\n Non-numeric character on index setion: possibly a typo or "
    "a weird bracket configuration (crash!)\n" + 146*"*" + "\n\n\n")

    par = argparse.ArgumentParser(description="Checks the syntax (open curly \
    brackets and non numeric characters on the index position) and saves a \
    reference for any error found in a text file (sc-result.txt). \
    Any line break inside brackets or dev comments that don't start with the \
    usual number sign will raise a false positive (you can use lbr to \
    minimaze false positives. You'll have to fix any syntax error manually \
    using the output text as reference. There are two modes, normal and full. \
    Full mode adds the line number to any flag encountered, but unfortunately \
    it also makes the script very slow.")
    mode = par.add_mutually_exclusive_group()
    par.add_argument("target", help="Target folder")
    mode.add_argument("-f", "--fullmode", action="store_true", help="Full mode")
    args = par.parse_args()

    path = os.path.abspath(args.target)
    dirname = os.path.basename(path)
    thefiles = pathfinder(path, excluded = ["__pycache__"])

    if not thefiles:
        sys.exit("There are no .msg files.")

    enc = encfinder(dirname)

    print("+ Working with %s (%s)..." % (dirname, enc))

    output = syntax_checker(thefiles, enc, fullmode=args.fullmode)
    if output:
        output = help_msg + output
        with open('sc-result-%s.txt' % dirname, 'w', encoding=enc) as foutput:
            foutput.write(output)
        print("There are syntax errors!")
    else:
        print("No syntax errors found!")
