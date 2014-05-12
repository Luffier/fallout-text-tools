import os, re, fnmatch

thefiles = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.msg'):
        thefiles.append(os.path.join(root, filename))
      
      
j = '\n'
s = '='
b = ' '
currentp = 0
result = ''
files_left = len(thefiles)


description = "\n\
This script opens Fallout's .msg files, checks the syntax (open curly brackets)\n\
and saves a reference for any error found in a text file called 'result.txt'.\n\
Remember that big files (more than 1000 lines) will take much more time.\n\
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

if thefiles:  
    startcheck()
else: 
    print(no_files_msg)
    input()
    exit()

print ('\n\nWORKING...\n\n')

for file in thefiles:

    filename = file[::-1] # reverse the filename (currently a path)
    filename = filename[:filename.index('\\')] # removes everything until the last slash, leaviang only the filename
    filename = filename[::-1] # reverse again
    
    header = (len(filename)+32)*s + j + 12*s + filename + "  BEGINS" + 12*s + j + (len(filename)+32)*s + 4*j
    
    openedfile = open(file, 'r')
    text = openedfile.read()
    characters = list(text)
    
    #currentp represents the current position of the character being processed
    while characters[currentp:]:
        if characters[currentp] == '{':
            currentp = currentp + 1
            while characters[currentp:]:
                if characters[currentp] == '}':
                    currentp = currentp + 1
                    break
                elif characters[currentp] == '{':
                    result = result + header + text[:currentp] + "<-- ERROR HERE \n\n\n\n\n"
                    break
                else: 
                    currentp = currentp + 1
                    if not characters[currentp:]:
                        result = result + header + text[:currentp] + "<-- ERROR HERE \n\n\n\n\n"
                        break
        elif characters[currentp] == '}':
            currentp = currentp + 1
            result = result + header + text[:currentp] + "<-- ERROR HERE \n\n\n\n\n"
        else:
            currentp = currentp + 1
    currentp = 0
    files_left = files_left - 1
    openedfile.close()
    
    fbars = 43-len(filename) # bars to give a nice looking format
    print (filename + " CHECKED " + "-"*fbars + '>  ' + str(files_left) + " files left.")

if not result:
    result = "\n\nDONE! All files have correct syntax!"
    print (result)
    with open('result.txt','w') as fresult:
        fresult.write(result)
        
else:
    result = "Look for the 'ERROR HERE' lines to find where the errors are located.\n\n\n" + result
    print ("\n\nDONE! There are syntax errors!")
    with open('result.txt','w') as fresult:
        fresult.write(result)

input()