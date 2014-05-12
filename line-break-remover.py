import os, re, fnmatch

thefiles = []
for root, dirnames, filenames in os.walk('.'): 
    if 'out' in dirnames: dirnames.remove('out')
    for filename in fnmatch.filter(filenames, '*.msg'):
        thefiles.append(os.path.join(root, filename))

thefiles[:] = [file for file in thefiles if not file.lower().endswith(('fke_dude.msg', 'deadcomp.msg'))]

description = "\n\
This script opens Fallout .msg files, looks for break lines,\n\
removes them and saves the changes (with the same directory structure)\n\
in a directory called 'out'. This will also remove unnecessary spaces.\n\
Both fke_dude.msg and deadcomp.msg are excluded.\n\
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


def createdirs():
    if not os.path.exists('out'):
        os.makedirs('out')
    for file in thefiles:       
        dirpath = file[::-1]
        dirpath = dirpath[dirpath.index('\\'):]
        dirpath = dirpath[::-1]
        dirpath = '.\\out' + dirpath[1:]
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            

if thefiles:
    startcheck()
else: 
    print(no_files_msg)
    input()
    exit()

createdirs()

print ("\n\nWORKING...\n\n")

for file in thefiles:

    fileout_path = '.\\out' + file[1:]
    
    with open(file, 'r') as filein:
        lines = filein.readlines()
        
    fileout = open(fileout_path, 'w')
    
    for line in lines:
        
        m1 = re.findall(r'\}[ ]*$',line) #not empty for normal -single- lines
        m2 = re.findall(r'\}[ ]*\#.*$',line) #not empty for lines with inline dev comments
        
        #removes any space after the final closing bracket
        line = re.sub(r'(\})[ ]*$', r'\1', line)
            
        #dev comment line
        if line.startswith('#'):
            fileout.write(line)
            
        #line with inline dev comment; could be merge with the above
        elif m2:
            #removes any space after the inline dev comment
            line = re.sub(r'[ ]*$', '', line)
            fileout.write(line)
        
        #needed for some reason
        elif line == '\n':
            fileout.write('\n')
        
        #line with an open bracket and a line break (main goal)
        elif not m1:
            fileout.write(line.replace('\n',''))

        #write if it doesn't fit the above categories
        else: 
            fileout.write(line)
    
    fileout.close()

print ("DONE!")
input()