import os, shutil, re, fnmatch


def pathfinder(target = '.', excludedirs = []):
    filespaths = []
    for root, dirnames, filenames in os.walk(target):
        
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
        custom = False
    elif inputcheck in ('c','custom'):
        custom = True
    else:
        exit()
    return custom


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
    
    return inputcheck_ex, inputcheck_mode

    
def dircreator(files, output_root):
    
    ndirs = 0
    
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    for file in files:
        
        fullpath = os.path.dirname(file)
        dirpath = os.path.join('.', output_root, fullpath[2:])
        
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            ndirs = ndirs + 1
    
    return ndirs
    
#if allmode is False it will write only files with changes
def linebreak_remover(files, output_root, excluded = [], allmode = False, clsmode = False):
    
    files_changed = 0
    deleted_spaces = 0
    deleted_linebreaks = 0
    
    #if not argument given Python treats it as a False; it needs to be an empty list
    if not excluded: 
        excluded = []

    for file in files:
        
        fileout_path = os.path.join('.', output_root, file[2:])
        filename = os.path.split(file)[-1]
        
        if filename.lower() in excluded:

            if allmode:
                shutil.copy(file, fileout_path)
            continue

        else:

            with open(file, 'r') as filein:
                lines = filein.readlines()

            filein_reference = ''.join(lines)
            
            fileout_text = ''

            for line in lines:
            
                if clsmode:
                    line = re.sub(r'\t', ' ' *4, line)
                    line = re.sub(r'\/\/', '#', line)
                
                m1 = re.findall(r'\}[ \t]*$', line) #not empty for normal -single- lines
                m2 = re.findall(r'\}[ \t]*\#.*$', line) #not empty for lines with inline dev comments
                m3 = re.findall(r'\}[ \t]*\/\/.*$', line) #not empty for lines with inline dev comments (alt. notation)

                #counts the number of unnecessary spaces/tabs before deleting them
                spaces = re.findall(r'\}([ \t]*)$', line)
                if spaces:
                    deleted_spaces = deleted_spaces + len(spaces[0])
                
                #removes any space after the final closing bracket
                line = re.sub(r'(\})[ \t]*$', r'\1', line)
           
                #dev comment line
                if line.startswith('#'):
                    fileout_text = fileout_text + line
                    
                    spaces = re.findall(r'([ \t]*)$', line)
                    if spaces:
                        deleted_spaces = deleted_spaces + len(spaces[0])
                    line = re.sub(r'[ \t]*$', '', line)
                    
                #line with inline dev comment; could be merge with the above
                elif m2 or m3:
                    
                    spaces = re.findall(r'([ \t]*)$', line)
                    if spaces:
                        deleted_spaces = deleted_spaces + len(spaces[0])
                    line = re.sub(r'[ \t]*$', '', line)
                    
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
                
                files_changed = files_changed + 1 
                with open(fileout_path, 'w') as fileout:
                    fileout.write(fileout_text)
            
            elif allmode:
               
               shutil.copy(file, fileout_path)
            
    return [len(files), len(excluded), files_changed, deleted_linebreaks, deleted_spaces]




if __name__ == "__main__":

    start_msg = "\n\
This script opens Fallout .msg files, looks for break lines,\n\
removes them and saves the changes (with the same directory structure)\n\
in a directory called 'output'. This will also remove unnecessary spaces.\n\
\n\
Default settings:\n\
* fke_dude.msg and deadcomp.msg are excluded\n\
* the script will only output files with changes\n\
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

    thefiles = pathfinder(excludedirs = [outputdir])

    excluded_files = ['fke_dude.msg','deadcomp.msg']
    mode = False
    
    if thefiles:
        
        if startcheck(start_msg):
            excluded, mode = ( optionscheck( [exclusions_msg, mode_msg] ) )
            
            if excluded:
                excluded_files = excluded
        

    else:
        print(no_files_msg)
        input()
        exit()
    
    
    dircreator(thefiles, outputdir)


    print ("\n\nWORKING...\n\n")


    results = linebreak_remover(thefiles, outputdir, excluded = excluded_files, allmode = mode)

    
    print( 'Number of files: %i (%i excluded)' % (results[0], results[1]) )
    print( 'Number of files changed: %i' % results[2] )
    print( 'Line breaks toll: %i' % results[3] )
    print( 'Unnecessary spaces toll: %i' % results[4] )
    print ("\n\nDONE!")

    input()
