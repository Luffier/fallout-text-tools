import os, shutil, re, fnmatch

from main import pathfinder, encfinder, treecreator, listdirs, alt_open


#if allmode is False it will write only files with changes
def linebreak_remover(files, output_root, enc = None, excluded = [], allmode = False, clsmode = False):

    files_changed = 0
    deleted_spaces = 0
    deleted_linebreaks = 0
    isBetweenBrackets = False


    for afile in files:

        fileout_path = os.path.join('.', output_root, afile[2:])
        filename = os.path.split(afile)[-1]

        if filename.lower() in excluded:

            if allmode:
                shutil.copy(afile, fileout_path)
            continue

        else:
            par = [enc, None] #parameters = [enconding, errors]
            lines = alt_open(afile, par)

            filein_reference = ''.join(lines)
            fileout_text = ''

            for line in lines:

                if clsmode:
                    line = re.sub(r'\t', '    ', line)
                    line = re.sub(r'\/\/', '#', line)
                    line = re.sub(r'^[ ]*(\{[0-9]+\}\{.*\}\{[^{]*\})[^\}\{\r\n\t#\/ a-zA-Z0-9]+(.*)', r'\1\2', line)

                if line.startswith('{'): isBetweenBrackets = True

                m1 = re.findall(r'\}[ \t\u3000]*$', line) #not empty for normal -single- lines
                m2 = re.findall(r'\}[ \t\u3000]*\#.*$', line) #not empty for lines with inline dev comments
                m3 = re.findall(r'\}[ \t\u3000]*\/\/.*$', line) #not empty for lines with inline dev comments (alt. notation)

                #counts the number of unnecessary spaces/tabs before deleting them
                spaces = re.findall(r'\}([ \t\u3000]*)$', line)
                if spaces:
                    deleted_spaces = deleted_spaces + len(spaces[0])

                #removes any space after the final closing bracket
                line = re.sub(r'(\})([ \t\u3000]*)$', r'\1', line)

                #removes any space before the initial bracket
                line = re.sub(r'^([ \t\u3000]*)(\{)', r'\2', line)

                #line with normal or inline dev comment
                if line.startswith('#') or m2 or m3:
                    spaces = re.findall(r'([ \t\u3000]*)$', line)
                    if spaces:
                        deleted_spaces = deleted_spaces + len(spaces[0])
                    line = re.sub(r'([ \t\u3000]*)$', '', line)
                    fileout_text = fileout_text + line
                    isBetweenBrackets = False

                elif line == '\n' and not isBetweenBrackets:
                    fileout_text = fileout_text + '\n'

                #line with an open bracket and a line break (main goal)
                elif not m1 and isBetweenBrackets:
                    fileout_text = fileout_text + line.replace('\n','')
                    deleted_linebreaks = deleted_linebreaks + 1

                #write if it doesn't fit the above categories
                else:
                    fileout_text = fileout_text + line
                    isBetweenBrackets = False

            if fileout_text != filein_reference:

                files_changed = files_changed + 1
                with open(fileout_path, 'w', encoding=enc) as fileout:
                    fileout.write(fileout_text)

            elif allmode:

               shutil.copy(afile, fileout_path)

    return [len(files), len(excluded), files_changed, deleted_linebreaks, deleted_spaces]




if __name__ == '__main__':

    start_msg = "\n\
This script opens Fallout .msg files, looks for break lines,\n\
removes them and saves the changes (with the same directory structure)\n\
in a directory called 'output'. This will also remove unnecessary spaces.\n\
\n\
Default settings:\n\
* fke_dude, deadcomp and democomp are excluded\n\
* the script will only output files with changes\n\
\n\n\
[y]es to proceed, [c]ustom to change the settings or anything else to quit: "

    no_files_msg = "\n\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"

    exclusions_msg = "\n\
What files do you want to exclude (case insensitive)?, press Enter for none Ex: 'f1.msg f2.msg':\n"

    mode_msg = "\n\n\
Do you want the output to include all files (even those without changes)? [y]es or [n]o: "


    outputdir = 'lb-output'

    thefiles = pathfinder(excluded = [outputdir, '__pycache__'])

    excluded_files = ['fke_dude.msg', 'democomp.msg','deadcomp.msg']
    mode = False

    if thefiles:
        inputcheck = input(start_msg).lower()
        if inputcheck not in ('yes','y','c','custom'):
            exit()
        if inputcheck in ('c','custom'):
            excluded_files = input(exclusions_msg).lower().split()

            mode = input(mode_msg).lower()
            if mode in ('yes','y'):
                mode = True
            else:
                mode = False

    else:
        input(no_files_msg)
        exit()


    print ("\n\nWORKING...\n\n")

    treecreator(thefiles, outputdir)

    dirnames = listdirs(excluded = [outputdir, '__pycache__'])

    for dirname in dirnames:
        dirnames0 = [d for d in dirnames if d is not dirname]
        thefiles = pathfinder(excluded = [outputdir] + dirnames0)
        enc = encfinder(dirname)

        print( "\n+ Working with %s (%s)...\n\n" % (dirname, enc ) )

        results = linebreak_remover(thefiles, outputdir, enc = enc, excluded = excluded_files, allmode = mode)

        print( " - Number of files: %i (%i excluded)" % (results[0], results[1]) )
        print( " - Number of files changed: %i" % results[2] )
        print( " - Line breaks toll: %i" % results[3] )
        print( " - Unnecessary spaces toll: %i" % results[4] )
        print( "   %s completed!\n" % dirname )

    input("\nALL DONE!")
