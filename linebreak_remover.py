import os, re, fnmatch


def pathfinder():
    filespaths = []
    for root, dirnames, filenames in os.walk('.'):
        if 'out' in dirnames: dirnames.remove('out')
        for filename in fnmatch.filter(filenames, '*.msg'):
            filespaths.append(os.path.join(root, filename))
    return filespaths
    

def startcheck(message):
    inputcheck = input(message).lower()
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

            
def linebreak_remover():
    
    files_changed = 0
    deleted_spaces = 0
    deleted_linebreaks = 0
    
    for file in thefiles:
        
        fileout_path = '.\\out' + file[1:]
        
        with open(file, 'r') as filein:
            lines = filein.readlines()

        filein_reference = ''.join(lines)
        
        fileout_text = ''
        
        for line in lines:
            
            m1 = re.findall(r'\}[ ]*$', line) #not empty for normal -single- lines
            m2 = re.findall(r'\}[ ]*\#.*$', line) #not empty for lines with inline dev comments
            
            #counts the number of unnecessary spaces before deleting them
            spaces = re.findall(r'\}([ ]*)$', line)
            if spaces:
                deleted_spaces = deleted_spaces + len(spaces[0])
            
            #removes any space after the final closing bracket
            line = re.sub(r'(\})[ ]*$', r'\1', line)
       
            #dev comment line
            if line.startswith('#'):
                fileout_text = fileout_text + line
                
            #line with inline dev comment; could be merge with the above
            elif m2:
                
                #counts the number of unnecessary spaces before deleting them
                spaces = re.findall(r'([ ]*)$', line)
                if spaces:
                    deleted_spaces = deleted_spaces + len(spaces[0])

                #removes any space after the inline dev comment
                line = re.sub(r'[ ]*$', '', line)
                fileout_text = fileout_text + line
            
            #needed for some reason
            elif line == '\n':
                fileout_text = fileout_text + '\n'
            
            #line with an open bracket and a line break (main goal)
            elif not m1:
                fileout_text = fileout_text + line.replace('\n','')
                deleted_linebreaks = deleted_linebreaks + 1

            #write if it doesn't fit the above categories
            else: 
                fileout_text = fileout_text + line
        
        
        if fileout_text != filein_reference:
            
            files_changed = files_changed +1 
            with open(fileout_path, 'w') as fileout:
                fileout.write(fileout_text)
            
    
    return (len(thefiles), files_changed, deleted_linebreaks, deleted_spaces)
  
  
if __name__ == "__main__":

    start_msg = "\n\
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


    thefiles = pathfinder()
    excluded = ('fke_dude.msg', 'deadcomp.msg')
    thefiles[:] = [file for file in thefiles if not file.lower().endswith(excluded)]

    if thefiles:  
        startcheck(start_msg)
    else: 
        print(no_files_msg)
        input()
        exit()

    createdirs()

    print ("\n\nWORKING...\n\n")


    results = linebreak_remover()


    print('Number of files:           ' , results[0])  
    print('Number of files changed:   ' , results[1])
    print('Line breaks toll:          ' , results[2])
    print('Unnecessary spaces toll:   ' , results[3])
    print ("\n\nDONE!")

    input()
