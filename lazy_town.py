"""Makes the target localization files compatible with the latest Fixt update,
the result will be a mixture of English and the target language. Levenshtein
algorithm is used (if you don't have python-Levenshtein, difflib will be used,
and its results tend to be very different). You can change the default
threshold of 1 (lower similarity ratio). At a value of 1, it would only copie
lines that haven't changed. You could use  a slightly lower value to retain
lines with negligible changes. Creates a log of missing files and lines."""
import os, re, sys, shutil, argparse
import common
try:
    import Levenshtein
    def ratio(string1, string2):
        return Levenshtein.ratio(string1, string2)
except ImportError:
    import difflib
    def ratio(string1, string2):
        return difflib.SequenceMatcher(None, string1, string2).ratio()
    print("* python-Levenshtein module not found, using difflib instead *\n")
try:
    import ujson as json
except ImportError:
    import json
    print("* ujson module not found, using json instead *\n")

line_p = re.compile(r'^[^\S\n]*\{([0-9]+)\}\{(?:.*)\}\{([^{]*)\}')

#makes a dictionary with the content of .msg files found in a given dirpath
#dictionary structure: {'filename': {'index': 'line content'}}
def analyzer(dirpath, encoding=None, clearcache=False):

    cachepath = os.path.join('.', 'ftt-cache')
    os.makedirs(cachepath, exist_ok=True)
    dirname = os.path.basename(dirpath)
    cachepath = os.path.join(cachepath, '{}.json'.format(dirname))

    if not os.path.isfile(cachepath) or clearcache:
        data = {}
        filepaths = common.pathfinder(dirpath)

        for filepath in filepaths:
            filename = os.path.split(filepath)[-1]
            data[filename] = {}
            lines = common.readlines(filepath, encoding)
            for line in lines:
                if line_p.search(line):
                    line_sections = line_p.findall(line)[0]
                    try:
                        index = line_sections[0]
                        data[filename][index] = line_sections[1]
                    except IndexError:
                        print("There are syntax errors in:")
                        print("{:<7d}'{}'".format(lines.index(line), filepath))
                        sys.exit("Aborting...")

        with open(cachepath, 'w') as cacheout:
            json.dump(data, cacheout)

    else:
        print("Using cached language data ({})".format(dirname))
        with open(cachepath, 'r') as cachein:
            data = json.load(cachein)
    return data

#base => English files used during the localization process
#base2 => current English files
#target => localization files
#merges base2 and target by comparing base and base2, if the two lines have
#a similarity ratio higher than the threshold value, the target content is used
def comparator(base, base2, target, thd=1):
    above_thd = 0
    below_thd = 0
    not_found = 0
    missing_files = 0
    log = ""

    target2 = base2

    for afile in base: #for every filename in base (original files)
        #only if it exists in base2 and target (Fixt/loc files)
        if base2.get(afile) and target.get(afile):
            for index in base[afile]: #for every index in filename
                if base2[afile].get(index): #only if line exists in Fixt
                    #if the dif. ratio between the two is above the thd
                    if ratio(base[afile][index], base2[afile][index]) >= thd:
                        #and the localization is complete
                        if target[afile].get(index):
                            #the old content is copied (main goal)
                            target2[afile][index] = target[afile][index]
                            above_thd += 1
                        else:
                            log += "Content not found in target: "
                            log += "({} {})\n".format(afile, index)
                            not_found += 1
                    else:
                        below_thd += 1
        else:
            log += "Missing file in target or Fixt: ({})\n".format(afile)
            missing_files += 1

    print("There were {:d} lines above the threshold".format(above_thd))
    print("There were {:d} lines below the threshold".format(below_thd))
    print("There are {:d} lines missing.".format(not_found))
    print("There are {:d} files missing".format(missing_files))
    with open('lt-log.txt', 'w') as flog:
        flog.write(log)

    return target2

#copies the dictionary's content into the .msg files inside dirpath
#this way we can keep comments and structure
def injector(lang, dirpath, encoding):

    dirname = os.path.basename(dirpath)[:-4]
    filepaths = common.pathfinder(dirpath)
    target_enc = common.encfinder(dirname)

    for filepath in filepaths:
        text_out = ''
        filename = os.path.split(filepath)[-1]
        lines = common.readlines(filepath, encoding)
        for line in lines:
            if line_p.search(line):
                line_sections = line_p.search(line)
                index = line_sections.group(1)
                if (index in lang[filename]) and line_sections.group(2):
                    line = (line[:line_sections.start(2)] +
                            lang[filename][index]         +
                            line[line_sections.end(2):])
                text_out += line
            else:
                text_out += line

        common.writelines(filepath, target_enc, text_out)


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("base", default="ENGLISH_BASE",
                     help="English files used during the \
                     localization process (folder name)")
    par.add_argument("base2", default="ENGLISH_FIXT",
                     help="Current English files (folder name)")
    par.add_argument("target", help="Target files (folder name)")
    par.add_argument("-t", "--threshold", type=float, default=1,
                     help="Lower similarity ratio threshold")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    for dirpath in (args.base, args.base2):
        dirname = os.path.basename(dirpath)
        if not os.path.isdir(dirname):
            sys.exit("\n{} folder missing. Aborting.".format(dirname))

    target2_path =  os.path.join('.', args.target + '_NEW')
    if os.path.isdir(target2_path):
        shutil.rmtree(target2_path)

    base_enc = common.encfinder(args.base)
    target_enc = common.encfinder(args.target)

    print("\n\nWORKING...\n\n")

    base_lang = analyzer(args.base, base_enc, args.clearcache)
    base2_lang = analyzer(args.base2, base_enc, args.clearcache)
    target_lang = analyzer(args.target, target_enc, args.clearcache)

    target2_lang = comparator(base_lang, base2_lang, target_lang,
                                 args.threshold)

    shutil.copytree(args.base2, target2_path)
    injector(target2_lang, target2_path, base_enc)

    print("\n\nALL DONE!\n\n")
    sys.exit()
