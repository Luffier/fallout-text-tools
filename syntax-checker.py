import os, re, fnmatch

thefiles = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.msg'):
        thefiles.append(os.path.join(root, filename))

result = ''

description = "\n\
This script opens Fallout's .msg files, checks the syntax (open curly brackets)\n\
and saves a reference for any error found in a text file called 'SC-result'\n\
This version is much quicker and reliable but any line break inside brackets\n\
or dev comments that don't start with the usual number sign will raise\n\
a false positive. Use the line-break-remover to minimaze the false positives.\n\
You'll have to solve the problem manually, using the output text as reference.\n\
\n\
\n\
Type [y]es and hit enter to proceed or anything else to quit: "

no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"

help_msg = 174*"*" + "\n  Less tran three pairs of brackets: line break inside brackets (false positive), dev comment without number sign (ugly) or missing bracket/s (it would have cause a crash!)  \n\
  More than three pairs of brackets: inline dev comment with brackets or two lines in one (not fatal but ugly)  \n" + 174*"*" + "\n\n\n"


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

print ("\n\nWORKING...\n\n")

for file in thefiles:
    
    occurrence = False
    
    with open(file, 'r') as rfile:
        lines = rfile.readlines()
    
    
    lines = [line for line in lines if line.startswith('#') is False]
    lines = [line for line in lines if line != '\n']
    lines = [line for line in lines if line]
    
    for line in lines:
        brackets = [character for character in line if character in ('{','}')]
        brackets = ''.join(brackets)
        pairs = re.findall(r'\{\}', brackets)
        
        if len(pairs) != 3 and occurrence == False:
            occurrence = True
            result = result + file + "\n"
            
        if len(pairs) < 3:
            result = result + "        Less tran three pairs -->   " + "'" + line.replace('\n','') + "'\n"
            
        elif len(pairs) > 3:
            result = result + "        More than three pairs -->   " + "'" + line.replace('\n','') + "'\n"
    
    if occurrence == True:
        result = result + "\n\n"
    
    occurrence = False

if not result:
    result = "\n\nDONE! All files have correct syntax!"
    print (result)

else:
    result = help_msg + result
    print ("\n\nDONE! There are syntax errors!")
    with open('SC-result.txt','w') as fresult:
        fresult.write(result)

input()