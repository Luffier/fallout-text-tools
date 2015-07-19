import os, re, fnmatch

from main import pathfinder, encfinder, listdirs


def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'):
        pass
    else:
        exit()


def syntax_checker(files, enc):
    result = ''

    for afile in files:
        print(afile)
        occurrence = False
        e = None
        while True:
            with open(afile, 'r', encoding=enc, errors=e) as filein:
                try:
                    lines = filein.readlines()
                    break
                except UnicodeDecodeError:
                    print(afile + "\n  ---> There was a decoding error in this file (ignoring for now)\n")
                    e = 'ignore'

        reference = lines

        lines = [line for line in lines if not re.findall(r'^[ ]*#', line)]
        lines = [line for line in lines if line != '\n']
        lines = [line for line in lines if not re.findall(r'^[ ]+$', line)]
        lines = [line for line in lines if line]

        for line in lines:
            brackets = [character for character in line if character in ('{','}')]
            brackets = ''.join(brackets)
            npairs = brackets.count('{}')

            if re.findall(r'[ ]*\{.*([^0-9]+).*\}\{.*\}\{[^{]*\}', line):
                result = result + "        Wrong character/s on index setion  -->  Line %i  -->  '%s'\n" % (reference.index(line)+1, line.replace('\n',''))

            if npairs != 3 and not occurrence:
                occurrence = True
                result = result + afile + "\n"

            if npairs < 3:
                result = result + "        Less tran three pairs  -->  Line %i  -->  '%s'\n" % (reference.index(line)+1, line.replace('\n',''))

            elif npairs > 3:
                result = result + "        More than three pairs  -->  Line %i  -->  '%s'\n" % (reference.index(line)+1, line.replace('\n',''))

        if occurrence:
            result = result + "\n\n"

        occurrence = False
    return result




if __name__ == '__main__':

    start_msg = "\n\
This script opens Fallout's .msg files, checks the syntax (open curly brackets)\n\
and saves a reference for any error found in a text file called 'sc-result'\n\
This version is much quicker and reliable but any line break inside brackets\n\
or dev comments that don't start with the usual number sign will raise\n\
a false positive. Use the line-break-remover to minimaze the false positives.\n\
You'll have to fix any syntax error manually, using the output text as reference.\n\
\n\n\
[y]es and hit enter to proceed or anything else to quit: "

    no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"

    help_msg = 175*"*" + "\n  Less tran three pairs of brackets: line break \
inside brackets (false positive), dev comment without number sign (ugly) or \
missing bracket/s (it would have cause a crash!)  \n More than three pairs of \
brackets: inline dev comment with brackets inside, two lines in one (not fatal \
but ugly) or a 'lost' set of brackets (it would have cause a crash!) \n        \
                      Wrong character/s on index setion: possibly a typo or a \
weird bracket configuration (it would have cause a crash!)                    \
          \n" + 175*"*" + "\n\n\n"


    thefiles = pathfinder(excludedirs = ['__pycache__'])
    outputdir = 'output'

    if thefiles:
        startcheck(start_msg)
    else:
        input(no_files_msg)
        exit()

    print ("\n\nWORKING...\n\n")

    dirnames = listdirs(excluded = ['__pycache__'])

    for dirname in dirnames:
        dirnames0 = [d for d in dirnames if d is not dirname]
        thefiles = pathfinder(excludedirs = [outputdir] + dirnames0)
        enc = encfinder(dirname)

        output = syntax_checker(thefiles, enc)

        if not output:
            output = "DONE! All files have correct syntax!"
            print (output)

        else:
            output = help_msg + output

            with open('sc-result-%s.txt' % dirname, 'w', encoding=enc) as foutput:
                foutput.write(output)

    input("\n\nALL DONE! There are syntax errors!")
