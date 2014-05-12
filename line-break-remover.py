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
in a directory called 'out'. fke_dude.msg and deadcomp.msg excluded.\n\
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

print ("\n\nWORKING... \n\n")

for file in thefiles:
    filename = file[::-1]
    filename = filename[:filename.index('\\')]
    filename = filename[::-1]
    outpathf = '.\\out' + file[1:]
    
    with open(file, 'r') as filein:
        lines = filein.readlines()
        
    fileout = open(outpathf, 'w')
    
    for line in lines:
        ma = re.findall(r'\#',line) #line with inline dev commet
        mb = re.findall(r'\}$',line)
        if line.startswith('#'):
            fileout.write(line)
        elif line == '\n':
            fileout.write('\n')
        elif ma:
            fileout.write(line)
        elif not mb:
            fileout.write(line.replace('\n',''))
        else: fileout.write(line)
    
    fileout.close()

print ("DONE!")
input()