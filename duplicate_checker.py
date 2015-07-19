import os, re, fnmatch


from main import pathfinder, encfinder, listdirs


def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'):
        pass
    else:
        exit()


def duplicate_checker(files, enc):

    result = ''

    for afile in files:
        e = None
        while True:
            with open(afile, 'r', encoding=enc, errors=e) as filein:
                try:
                    lines = filein.readlines()
                    break
                except UnicodeDecodeError:
                    print(afile + "\n  ---> There was a decoding error in this file (ignoring for now)\n")
                    e = 'ignore'

        #remove dev comments and others
        lines = [line for line in lines if line.startswith('#') is False]
        lines = [line for line in lines if line.startswith('{') is True]

        indices = [re.findall(r'^[ ]*\{([0-9]+)\}', line)[0] for line in lines]
        indices = [int(index) for index in indices]

        #fills matches if there's any duplicate and records it
        matches = [index for index in indices if indices.count(index) > 1]
        if matches:
            result = result + afile
            matches.sort()
            while matches:
                result = result + "\n       This file has the index number %s repeated %s times!" % ( str(matches[0]), str(matches.count(matches[0])) )
                matches[:] = [match for match in matches if match != matches[0]]
            result = result + "\n\n"

    return result




if __name__ == '__main__':

    start_msg = "\n\
This script checks Fallout's .msg files for duplicates in the index numbers.\n\
The result will be saved into a text file called 'dc-result'. \n\
The script doesn't take into account the index numbers inside dev comments.\n\
\n\n\
[y]es and hit enter to proceed or anything else to quit: "

    no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"


    thefiles = pathfinder(excludedirs = ['__pycache__'])
    outputdir = 'output'

    if thefiles:
        startcheck(start_msg)
    else:
        print(no_files_msg)
        input()
        exit()


    print ("\n\nWORKING...\n\n")

    dirnames = listdirs(excluded = ['__pycache__'])

    for dirname in dirnames:
        dirnames0 = [d for d in dirnames if d is not dirname]
        thefiles = pathfinder(excludedirs = [outputdir] + dirnames0)
        enc = encfinder(dirname)
        output = duplicate_checker(thefiles, enc)

        if output:
            print("DONE! There are duplicate lines!")
            with open('dc-result-%s.txt' % dirname, 'w', encoding=enc) as foutput:
                foutput.write(output)


    input("DONE! Congratulations, there are no duplicate lines!")
