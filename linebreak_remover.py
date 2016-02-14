import os, re, sys, shutil, argparse

from common import *


#if fullmode is False it will write only files with changes
def linebreak_remover(target, enc = None, excluded = [], fullmode = False, ecmode = False):

    files_changed = 0
    deleted_spaces = 0
    deleted_linebreaks = 0
    isBetweenBrackets = False

    thefiles = pathfinder(target, excluded = ["lb-output", '__pycache__'])

    for afile in thefiles:
        foutput_path = os.path.join("lb-output", afile)
        filename = os.path.split(afile)[-1]

        if filename.lower() in excluded:

            if fullmode:
                shutil.copy(afile, foutput_path)
            continue

        else:
            par = [enc, None] #parameters = [enconding, errors]
            lines = alt_read(afile, par)

            filein_reference = ''.join(lines)
            fileout_text = ''

            for line in lines:

                if ecmode:
                    line = re.sub(r'\t', '    ', line) #tabs to 4 spaces
                    line = re.sub(r'\/\/', '#', line) #C like comments to the usual number sign
                    line = re.sub(r'^[ ]*(\{[0-9]+\}\{.*\}\{[^{]*\})[^\}\{\r\n\t#\/ a-zA-Z0-9]+(.*)', r'\1\2', line)
                    #uncommented text outside brackets

                if line.startswith('{'): isBetweenBrackets = True

                m1 = re.findall(r'\}[ \t\u3000]*$', line) #not empty for normal -single- lines
                m2 = re.findall(r'\}[ \t\u3000]*\#.*$', line) #not empty for lines with inline dev comments
                m3 = re.findall(r'\}[ \t\u3000]*\/\/.*$', line) #not empty for lines with inline dev comments (alt. notation)
                m4 = re.findall(r'\}[ ]*([^ \{\}\#\/\s])+.*$', line) #not empty for lines with text outside comments or brackets

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

                elif m4:
                    fileout_text = fileout_text + line

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
                with open(foutput_path, 'w', encoding=enc) as fileout:
                    fileout.write(fileout_text)

            elif fullmode:
               shutil.copy(afile, foutput_path)

    return (len(thefiles), len(excluded), files_changed, deleted_linebreaks, deleted_spaces)


if __name__ == '__main__':

    par = argparse.ArgumentParser(description="Looks for line breaks and \
    removes them, saves the results in the output folder (with the same \
    directory structure). This will also remove unnecessary spaces. Certain \
    files are excluded by default (fke_dude, deadcomp and democomp) but you \
    can chage them. Also you can choose to copy all files or only those with \
    changes.")
    par.add_argument("target", help="Target folder")
    par.add_argument("-f", "--fullmode", action="store_true",
                     help="Full mode, copies all files (even those \
                     without changes)")
    par.add_argument("-c", "--ecmode", action="store_true",
                     help="Extra cleaning mode, it removes tabs, uncommented \
                     text and replaces double slash for number sign. \
                     You should recheck the results if you use this mode.")
    par.add_argument("-r", "--recursive", action="store_true",
                      help="Recursive folder search; the target path should \
                      contain the localization folders you want to check")
    par.add_argument("-e", "--excluded", nargs="*",
                     default=['fke_dude.msg', 'democomp.msg','deadcomp.msg'],
                     help="List of excluded files (use lowercase, extension \
                     and separate with spaces)")
    args = par.parse_args()

    thefiles = pathfinder(excluded = ["lb-output", '__pycache__'])
    treecreator(thefiles, "lb-output")

    path = os.path.abspath(args.target)
    if not args.recursive:
        dirnames = [os.path.basename(path)]
    else:
        dirnames = listdirs(path, excluded = ["lb-output", '__pycache__'])

    for dirname in dirnames:
        other_dirs = [d for d in dirnames if d is not dirname]
        enc = encfinder(dirname)

        print( "\n+ Working with %s (%s)..." % (dirname, enc ) )

        results = linebreak_remover(dirname, enc, args.excluded, args.fullmode, args.ecmode)

        print( " - Number of files: %i (%i excluded)" % (results[0], results[1]) )
        print( " - Number of files changed: %i" % results[2] )
        print( " - Line breaks toll: %i" % results[3] )
        print( " - Unnecessary spaces toll: %i" % results[4] )
        print( "   %s completed!\n" % dirname )
