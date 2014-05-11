import os, re, fnmatch

thefiles = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.msg'):
        thefiles.append(os.path.join(root, filename))

result = ''

description = "\n\
This script checks Fallout .msg files for duplicates in the index numbers.\n\
The result will be saved into a text file. The script doesn't take into account\n\
the index numbers in the dev comments inside the .msg files.\n\
\n\
\n\
Type [y]es and hit enter to proceed or anything else to quit:"



def startcheck():
	inputcheck = input(description).lower()
	if inputcheck in ('yes','y'): pass
	else: exit()


# The nformat funtion opens and reads a file (parameter), and creates a string based in its content, ignoring lines that start with "#" (dev comments).  
# Then looks for something like this '{100}{' (or "left curly bracket"; "at least one number"; "right curly bracket"; "left curly bracket"),
# and returns a list of the numbers between the curly brackets.  

def nformat(file):
    rfile = open(file, 'r')
    lines = rfile.readlines()
    lines = [line for line in lines if line.startswith('#') is False]
    for x in range(len(lines)):
        if len(re.findall(r'\{([0-9]+)\}', lines[x])) > 1:
            lines[x] = re.findall(r'\{([0-9]+)\}', lines[x])[0]
    lines = ' '.join(lines)
    lines = re.findall(r'\{([0-9]+)\}', lines)
    lines = [int(e) for e in lines]
    rfile.close()
    return lines

    
    
startcheck()


print ('\n\nWORKING... \n\n')


# Runs nformat in every file and then looks for duplicates. If any occurrences are found, they are recorded in the variable result.


for file in thefiles:
    numbers = []
    numbers = nformat(file)
    occurrences = [x for x in numbers if numbers.count(x) > 1]
    if len(occurrences) > 0:
        result = result + file
        occurrences.sort()
        while occurrences != []:
            result = result + '\n       This file has the index number ' + str(occurrences[0]) + ' repeated ' + str(occurrences.count(occurrences[0])) + ' times!'
            occurrences[:] = [e for e in occurrences if e != occurrences[0]]
        result = result + '\n\n'

if result == '': 
    print('\nCongratulations, there are no duplicate lines!')
    fresult = open('result.txt','w')
    fresult.write('Congratulations, there are no duplicate lines!')
    fresult.close()
else:    
    fresult = open('result.txt','w')
    fresult.write(result + '\n')
    fresult.close()

print ("\n\nDONE!")
input()