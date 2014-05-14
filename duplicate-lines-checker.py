import os, re, fnmatch

thefiles = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.msg'):
        thefiles.append(os.path.join(root, filename))

start_msg = "\n\
This script checks Fallout's .msg files for duplicates in the index numbers.\n\
The result will be saved into a text file called 'dlc-result'. \n\
The script doesn't take into account the index numbers inside dev comments.\n\
\n\
\n\
Type [y]es and hit enter to proceed or anything else to quit: "

no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"


def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'): pass
    else: exit()

    
def duplicate_lines_checker(files):
    
    result = ''
    
    for file in files:
        
        with open(file, 'r') as rfile:
            lines = rfile.readlines()
        
        #remove dev comments and others
        lines = [line for line in lines if line.startswith('#') is False]
        lines = [line for line in lines if line.startswith('{') is True]
        
        indices = [re.findall(r'^\{([0-9])+\}', line)[0] for line in lines]
        indices = [int(index) for index in indices]
        
        #fills matches if there's any duplicate and records it
        matches = [index for index in indices if indices.count(index) > 1]
        if matches:
            result = result + file
            matches.sort()
            while matches:
                result = result + "\n       This file has the index number " + str(matches[0]) + " repeated " + str(matches.count(matches[0])) + " times!"
                matches[:] = [match for match in matches if match != matches[0]]
            result = result + "\n\n"
    
    return result
    


if thefiles:  
    startcheck(start_msg)
else: 
    print(no_files_msg)
    input()
    exit()


print ("\n\nWORKING...\n\n")



output = duplicate_lines_checker(thefiles)



if not output:
    print("DONE! Congratulations, there are no duplicate lines!")
    
else:
    print("DONE! There are duplicate lines!")
    with open('dlc-result.txt','w') as foutput:
        foutput.write(output)

        
        
input()