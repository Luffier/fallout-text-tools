"""Looks for line breaks and removes them, saves the results in the output
folder (with the same directory structure). This will also remove unnecessary
spaces. Certain files are excluded by default (fke_dude, deadcomp and democomp)
but you can chage them. You can also choose to copy all files or only those
with changes."""
import os, re, sys, shutil, argparse
from os.path import basename
import common


#fullmode also copies files without changes
#ecmode converts tabs to spaces (4), and // to #
def linebreak_remover(target, encoding = None, excluded = [],
                      fullmode = False, ecmode = False):

    log = {"files":    0,
    "files_excluded":  0,
    "files_changed":   0,
    "spaces_toll":     0,
    "linebreaks_toll": 0}

    dirpath_out = os.path.join(".", "lb-output", basename(target))
    try:
        shutil.rmtree(dirpath_out)
    except FileNotFoundError:
        pass

    shutil.copytree(target, dirpath_out)
    filepaths = common.pathfinder(dirpath_out, excluded=["lb-output"])

    excluded = [f for f in filepaths if basename(f).lower() in excluded]
    filepaths = [f for f in filepaths if f not in excluded]

    log["files"] = len(filepaths)
    log["files_excluded"] = len(excluded)

    for filepath in filepaths:
        filename = basename(filepath)
        lines = common.readlines(filepath, encoding)
        text_reference = ''.join(lines)
        text_out = ''
        startsWithBracket = False

        for line in lines:
            if ecmode:
                #tabs to 4 spaces (default in Fallout?)
                line = re.sub(r'\t', '    ', line)
                #C like comments to the usual number sign
                line = re.sub(r'\/\/', '#', line)

            #line starts with an opening bracket (excludes whitespaces)
            startsWithBracket = re.search(r'^[^\S\n]*\{', line)
            endsWithBracket = re.search(r'\}[^\S\n]*$', line)
            #line starts with comments
            normalComment = re.search(r'^[^\S\n]*(?:\#+|(?:\/\/)+)', line)
            #line with inline dev comments of either format
            inlineComment = re.search(r'\}[^\S\n]*(?:\#+|(?:\/\/)+).*$', line)
            #line with text outside comments or brackets
            uncommentedText = re.search(r'\}\s*([^\s\{\}\#\/])+.*$', line)
            #line with spaces at the beginning or end
            hasSpaces = re.search(r'(^[^\S\n]+)|([^\S\n]+$)', line)
            emptyLine = re.search(r'^\s+$', line)

            if startsWithBracket:
                isBetweenBrackets = True
            elif endsWithBracket:
                isBetweenBrackets = False

            #counting and removal of unnecessary whitespaces
            if hasSpaces:
                line_size = len(line)
                if emptyLine:
                    line = re.sub(r'^[^\S\n]+$', '', line)
                elif startsWithBracket or endsWithBracket:
                    #remove any space after the final closing bracket
                    line = re.sub(r'(\})([^\S\n]*)$', r'\1', line)
                    #remove any space before the initial bracket
                    line = re.sub(r'^([^\S\n]*)(\{)', r'\2', line)
                elif normalComment or inlineComment:
                    #remove any space at the end
                    line = re.sub(r'([^\S\n]*)$', '', line)
                log["spaces_toll"] += line_size - len(line)

            #good line
            if (normalComment or inlineComment) or (
                startsWithBracket and endsWithBracket):
                text_out += line
                isBetweenBrackets = False
            #empty line
            elif emptyLine and not isBetweenBrackets:
                text_out += '\n'
            #uncommented text after bracket
            elif uncommentedText:
                text_out += line
                isBetweenBrackets = False
            #main goal
            elif isBetweenBrackets and not endsWithBracket:
                text_out += line.replace('\n', '')
                log["linebreaks_toll"] += 1
            #if it doesn't fit the above categories
            #(uncommented text or a syntax error)
            else:
                text_out += line
                isBetweenBrackets = False

        if text_out != text_reference:
            log["files_changed"] += 1
            with open(filepath, 'w', encoding=enc) as foutput:
                foutput.write(text_out)
        elif not fullmode:
            os.remove(filepath)

    if not fullmode:
        for filepath in excluded:
            os.remove(filepath)

    #remove non .msg files
    other_files = common.pathfinder(dirpath_out, file_filter='*.[!m][!s][!g]')
    for filepath in other_files:
        os.remove(filepath)
    #remove empty folders
    dirpaths = [r for r, d, f in os.walk(dirpath_out, topdown=False)]
    for dirpath in dirpaths:
        try:
            os.rmdir(dirpath)
        except OSError:
            pass

    return log


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("target", help="Target folder")
    par.add_argument("-f", "--fullmode", action="store_true",
                     help=("Full mode, copies all files (even those \
                     without changes)"))
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
                     and separate with spaces). If you don't want to exclude \
                     anything, write it alone")
    args = par.parse_args()

    targetpath = os.path.abspath(args.target)
    if not args.recursive:
        dirnames = [basename(targetpath)]
    else:
        dirnames = common.listdirs(targetpath, excluded=["lb-output"])

    for dirname in dirnames:
        if args.recursive:
            dirpath = os.path.join(targetpath, dirname)
        else:
            dirpath = targetpath

        enc = common.encfinder(dirname)
        print("\n+ Working with {} ({})...".format(dirname, enc))
        log = linebreak_remover(dirpath, enc, args.excluded,
                                args.fullmode, args.ecmode)

        print((" -Number of files: {files} ({files_excluded} excluded)\n"
               " -Number of files changed: {files_changed}\n"
               " -Line breaks toll: {linebreaks_toll}\n"
               " -Unnecessary spaces toll: {spaces_toll}\n"
               "  {} completed!\n").format(dirname, **log))
