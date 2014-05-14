import os, re, fnmatch


def pathfinder(excludedirs = []):
    filespaths = []
    for root, dirnames, filenames in os.walk('.'):
        
        if excludedirs:
            for exclusion in excludedirs:
                if exclusion in dirnames:
                    dirnames.remove(exclusion)
        
        for filename in fnmatch.filter(filenames, '*.msg'):
            filespaths.append(os.path.join(root, filename))
    
    return filespaths
    

def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'): 
        csettings = False
    elif inputcheck in ('c','custom'): 
        csettings = True
    else: 
        exit()
    return csettings

#to be changed
def optionscheck(questions):
    answers = []
    
    inputcheck_ex = input(questions[0]).lower()
    
    if inputcheck_ex: 
        inputcheck_ex = tuple( inputcheck_ex.split() )
    else:
        inputcheck_ex = False
    
    inputcheck_mode = input(questions[1]).lower()
    
    if inputcheck_mode in ('yes','y'):
        inputcheck_mode = True
    else:
        inputcheck_mode = False
    
    return (inputcheck_ex, inputcheck_mode)

    
def dircreator(files, output_root):
    
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    for file in files:       
        
        dirpath = file[::-1]
        dirpath = dirpath[dirpath.index('\\'):]
        dirpath = dirpath[::-1]
        dirpath = '.\\' + output_root + dirpath[1:]
        
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

#if allmode is False it will write only files with changes
def linebreak_remover(files, output_root, allmode = False):
    
    files_changed = 0
    deleted_spaces = 0
    deleted_linebreaks = 0
    
    for file in files:
        
        fileout_path = '.\\' + output_root + file[1:]
        
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
        
        

        
        if not allmode:
            
            if fileout_text != filein_reference:
                files_changed = files_changed +1 
                
                with open(fileout_path, 'w') as fileout:
                    fileout.write(fileout_text)
        else:
            
            if fileout_text != filein_reference:
                files_changed = files_changed +1 
            
            with open(fileout_path, 'w') as fileout:
                fileout.write(fileout_text)
            
    
    return (len(files), files_changed, deleted_linebreaks, deleted_spaces)
  
  
if __name__ == "__main__":

    start_msg = "\n\
This script opens Fallout .msg files, looks for break lines,\n\
removes them and saves the changes (with the same directory structure)\n\
in a directory called 'output'. This will also remove unnecessary spaces.\n\
Both fke_dude.msg and deadcomp.msg are excluded by default.\n\
\n\n\
[y]es to proceed, [c]ustom to change the settings or anything else to quit: "

    no_files_msg = "\n\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"

    exclusions_msg = "\n\
What files do you want to exclude (case insensitive)? Ex: 'f1.msg f2.msg'\n"
    
    mode_msg = "\n\n\
Do you want the output to include all files (even those without changes)? "
    
    outputdir = 'output'

    thefiles = pathfinder([outputdir])

    if thefiles:  
        if startcheck(start_msg):
            options = ( optionscheck( [exclusions_msg, mode_msg] ) )
            excluded = options[0]
            mode = options[1]
    else: 
        print(no_files_msg)
        input()
        exit()
    if excluded:
        thefiles[:] = [file for file in thefiles if not file.lower().endswith(excluded)]
    
    dircreator(thefiles, outputdir)


    print ("\n\nWORKING...\n\n")


    results = linebreak_remover(thefiles, outputdir, mode)


    print('Number of files:           ' , results[0])  
    print('Number of files changed:   ' , results[1])
    print('Line breaks toll:          ' , results[2])
    print('Unnecessary spaces toll:   ' , results[3])
    print ("\n\nDONE!")

    input()
