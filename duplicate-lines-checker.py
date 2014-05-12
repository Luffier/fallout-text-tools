import os, re, fnmatch

thefiles = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.msg'):
        thefiles.append(os.path.join(root, filename))

result = ''

description = "\n\
This script checks Fallout's .msg files for duplicates in the index numbers.\n\
The result will be saved into a text file called 'DLC-result'. \n\
The script doesn't take into account the index numbers inside dev comments.\n\
\n\
\n\
Type [y]es and hit enter to proceed or anything else to quit: "

no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"


def startcheck():
    inputcheck = input(description).lower()
    if inputcheck in ('yes','y'): pass
    else: exit()


# The nformat funtion opens and reads a file (parameter), and creates a string based in its content, ignoring lines that start with "#" (dev comments).  
# Then looks for something like this '{100}{' (or "left curly bracket"; "at least one number"; "right curly bracket"; "left curly bracket"),
# and returns a list of the numbers between the curly brackets.  


def nformat(file):

    with open(file, 'r') as rfile:
        lines = rfile.readlines()
    
    lines = [line for line in lines if line.startswith('#') is False]
    
    # if there's an inline comment with an index number it will cut the line leaving only the first one.
    for line in lines:
        indexes = re.findall(r'\{([0-9]+)\}', line)
        if len(indexes) > 1:
            line = indexes[0]
            
    lines = ' '.join(lines)
    lines = re.findall(r'\{([0-9]+)\}', lines)
    lines = [int(index) for index in lines]
    
    return lines

    
if thefiles:  
    startcheck()
else: 
    print(no_files_msg)
    input()
    exit()


print ("\n\nWORKING...\n\n")


# Runs nformat in every file and then looks for duplicates. If any occurrences are found, they are recorded in the variable result.


for file in thefiles:
    indexes = []
    indexes = nformat(file)
    matches = [index for index in indexes if indexes.count(index) > 1]
    if len(matches) > 0:
        result = result + file
        matches.sort()
        while matches:
            result = result + "\n       This file has the index number " + str(matches[0]) + " repeated " + str(matches.count(matches[0])) + " times!"
            matches[:] = [match for match in matches if match != matches[0]]
        result = result + "\n\n"

if not result:
    result = "Congratulations, there are no duplicate lines!"
    print("DONE! " + result)

else:
    print("DONE! There are duplicate lines!")
    with open('DLR-result.txt','w') as fresult:
        fresult.write(result)

input()