import os, re, fnmatch

from main import *


#Looks for lines with brackets (after discarding comments and empty lines), pairs
#them and flags if there's more than 3 pairs or a non-numeric character is found
#on the index section.
def syntax_checker(files, enc, fullmode=True):
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
                result = result + afile + "\n"

            if match:
                if fullmode: result = result + reference.index(line)+1
                result = result + "        Non-numeric on index  -->  '%s'\n" % line.replace('\n','')

            if npairs < 3:
                if fullmode: result = result + reference.index(line)+1
                result = result + "        Less tran three pairs -->  '%s'\n" % line.replace('\n','')

            elif npairs > 3:
                if fullmode: result = result + reference.index(line)+1
                result = result + "        More than three pairs -->  '%s'\n" % line.replace('\n','')

        if flag: result = result + "\n\n"
        flag = False

    return result




if __name__ == '__main__':

    start_msg = "\n\
This script opens Fallout's .msg files, checks the syntax (open curly brackets \n\
and non numeric characters on the index position) and saves a reference for\n\
any error found in a text file called 'sc-result'. This version is much quicker\n\
and reliable but any line break inside brackets or dev comments that don't\n\
start with the usual number sign will raise a false positive (you can use lbr\n\
to minimaze false positives. You'll have to fix any syntax error manually using\n\
the output text as reference. There are two modes, normal and full. Full mode\n\
adds the line number to any flag encountered, but unfortunately it also makes\n\
the script very slow.\n\
\n\n\
Type [n]ormal or [f]ull and hit enter to proceed or anything else to quit: "

    no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"

    help_msg = 175*"*" + "\n  Less tran three pairs of brackets: line break \
inside brackets (false positive), dev comment without number sign (ugly) or \
missing bracket/s (it would have cause a crash!)  \n More than three pairs of \
brackets: inline dev comment with brackets inside, two lines in one (not fatal \
but ugly) or a 'lost' set of brackets (it would have cause a crash!) \n        \
                Non-numeric character on index setion: possibly a typo or a \
weird bracket configuration (it would have cause a crash!)                   \
       \n" + 175*"*" + "\n\n\n"

    outputdir = 'output'
    thefiles = pathfinder(excluded = [outputdir, '__pycache__'])

    if thefiles:
        inputcheck = input(start_msg).lower()
        if inputcheck in ('full','f'):
            mode = True
        elif inputcheck in ('normal','n'):
            mode = False
        else:
            exit()
    else:
        input(no_files_msg)
        exit()


    print ("\n\nWORKING...\n\n")

    dirnames = listdirs(excluded = [outputdir, '__pycache__'])

    for dirname in dirnames:
        other_dirs = [d for d in dirnames if d is not dirname]
        thefiles = pathfinder(excluded = other_dirs)
        enc = encfinder(dirname)

        print( "\n+ Working with %s (%s)...\n\n" % (dirname, enc ) )
        output = syntax_checker(thefiles, enc, fullmode=mode)

        if output:
            output = help_msg + output
            with open('sc-result-%s.txt' % dirname, 'w', encoding=enc) as foutput:
                foutput.write(output)

    input("\n\nALL DONE! There are syntax errors!")
