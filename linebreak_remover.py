"""Looks for line breaks and removes them, saves the results in the output
folder (with the same directory structure). This will also remove unnecessary
spaces. Certain files are excluded by default (fke_dude, deadcomp and democomp)
but you can chage them. You can also choose to copy all files or only those
with changes."""
import os, re, sys, shutil, argparse
import common


#if fmode is False it will write only files with changes
def linebreak_remover(target, enc = None, excluded = [],
                      fullmode = False, ecmode = False):

    nfiles = nspaces = nlinebreaks = 0
    isBetweenBrackets = False

    files = common.pathfinder(target, excluded=["lb-output"])
    outpath = os.path.join(".", "lb-output", os.path.basename(target))
    try:
        shutil.rmtree(outpath)
    except FileNotFoundError:
        pass

    excluded = [f for f in files if os.path.basename(f).lower() in excluded]
    files = [f for f in files if f not in excluded]

    if fullmode:
        for afile in excluded:
            foutpath = afile.replace(os.path.commonpath((target, afile)), "")
            foutpath = outpath + foutpath
            common.copy(afile, foutpath)

    for afile in files:
        foutpath = afile.replace(os.path.commonpath((target, afile)), "")
        foutpath = outpath + foutpath
        filename = os.path.basename(afile)

        lines = common.open2(afile, encoding=enc)
        text_reference = ''.join(lines)
        text_out = ''

        for line in lines:
            if ecmode:
                #tabs to 4 spaces (default in Fallout?)
                line = re.sub(r'\t', '    ', line)
                #C like comments to the usual number sign
                line = re.sub(r'\/\/', '#', line)
                #uncommented text outside brackets

            if line.startswith('{'):
                isBetweenBrackets = True
            #not empty for normal -single- lines
            m1 = re.findall(r'\}[ \t\u3000]*$', line)
            #not empty for lines with inline dev comments
            m2 = re.findall(r'\}[ \t\u3000]*\#.*$', line)
            #not empty for lines with inline dev comments (alt. notation)
            m3 = re.findall(r'\}[ \t\u3000]*\/\/.*$', line)
            #not empty for lines with text outside comments or brackets
            m4 = re.findall(r'\}[ ]*([^ \{\}\#\/\s])+.*$', line)

            #counts the number of unnecessary spaces/tabs before deleting them
            spaces = re.findall(r'\}([ \t\u3000]*)$', line)
            if spaces:
                nspaces += len(spaces[0])

            #removes any space after the final closing bracket
            line = re.sub(r'(\})([ \t\u3000]*)$', r'\1', line)

            #removes any space before the initial bracket
            line = re.sub(r'^([ \t\u3000]*)(\{)', r'\2', line)

            #line with normal or inline dev comment
            if line.startswith('#') or m2 or m3:
                spaces = re.findall(r'([ \t\u3000]*)$', line)
                if spaces:
                    nspaces += len(spaces[0])
                line = re.sub(r'([ \t\u3000]*)$', '', line)
                text_out += line
                isBetweenBrackets = False

            elif line == '\n' and not isBetweenBrackets:
                text_out += '\n'

            elif m4:
                text_out += line

            #line with an open bracket and a line break (main goal)
            elif not m1 and isBetweenBrackets:
                text_out += line.replace('\n', '')
                nlinebreaks += 1

            #write if it doesn't fit the above categories
            else:
                text_out += line
                isBetweenBrackets = False

        if text_out != text_reference:
            nfiles += 1
            while True:
                try:
                    with open(foutpath, 'w', encoding=enc) as foutput:
                        foutput.write(text_out)
                except FileNotFoundError:
                    os.makedirs(os.path.dirname(foutpath), exist_ok=True)
                    continue
                break
        elif fullmode:
            common.copy(afile, foutpath)

    return (len(files), len(excluded), nfiles, nlinebreaks, nspaces)


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
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
                     default=['fke_dude.msg', 'democomp.msg', 'deadcomp.msg'],
                     help="List of excluded files (use lowercase, extension \
                     and separate with spaces)")
    args = par.parse_args()

    path = os.path.abspath(args.target)
    if not args.recursive:
        dirnames = [os.path.basename(path)]
    else:
        dirnames = common.listdirs(path, excluded=["lb-output"])

    for dirname in dirnames:
        if args.recursive:
            dirpath = os.path.join(path, dirname)
        else:
            dirpath = path

        enc = common.encfinder(dirname)
        print("\n+ Working with {} ({})...".format(dirname, enc))
        log = linebreak_remover(dirpath, enc, args.excluded,
                                args.fullmode, args.ecmode)

        print(" -Number of files: {:d} ({:d} excluded)".format(log[0], log[1]))
        print(" -Number of files changed: {:d}".format(log[2]))
        print(" -Line breaks toll: {:d}".format(log[3]))
        print(" -Unnecessary spaces toll: {:d}".format(log[4]))
        print("  {:d} completed!\n".format(dirname))
