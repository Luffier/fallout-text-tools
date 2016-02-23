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
    ratio = lambda x, y: Levenshtein.ratio(x, y)
except ImportError:
    import difflib
    ratio = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
    print("python-Levenshtein module not found, using difflib instead")
try:
    import ujson
except ImportError:
    import json
    print("ujson module not found, using json instead")


#makes a dictionary with the content of .msg files found in a given dirpath
#dictionary structure: {'filename': {'index': 'line content'}}
def analyzer(dirpath, encoding=None, clearcache=False):

    dirname = os.path.basename(dirpath)
    if not os.path.isfile('{}.json'.format(dirname)) or clearcache:
        line_p = re.compile(r'^[^\S\n]*\{([0-9]+)\}\{(?:.*)\}\{([^{]*)\}')
        startsWithBracket_p = re.compile(r'^[^\S\n]*\{')

        data = {}
        filepaths = common.pathfinder(dirpath)

        for filepath in filepaths:
            filename = os.path.split(filepath)[-1]
            data[filename] = {}
            lines = common.open2(filepath, encoding)
            for line in lines:
                if startsWithBracket_p.search(line):
                    line_content = line_p.findall(line)[0]
                    try:
                        index = line_content[0]
                        data[filename][index] = line_content[1]
                    except IndexError:
                        print("There are syntax errors in:")
                        print("{:<7d}'{}'".format(lines.index(line), filepath))
                        sys.exit("Aborting...")

        with open('{}.json'.format(dirname), 'w') as cacheout:
            try:
                ujson.dump(data, cacheout)
            except NameError:
                json.dump(data, cacheout)

    else:
        with open('{}.json'.format(dirname), 'r') as cachein:
            try:
                data = ujson.load(cachein)
            except NameError:
                data = json.load(cachein)
    return data


#base => English files used during the localization process
#newbase => current English files
#target => localization files
#merges newbase and target by comparing base and newbase, if the two lines have
#a similarity ratio higher than the threshold value, the target content is used
def comparator(base, newbase, target, thd=0.9):
    above_thd = 0
    below_thd = 0
    not_found = 0
    missing_files = 0
    log = ""

    newtarget = newbase

    for afile in base: #for every filename in base (original files)
        #only if it exists in newbase and target (Fixt/loc files)
        if newbase.get(afile) and target.get(afile):
            for index in base[afile]: #for every index in filename
                if newbase[afile].get(index): #only if line exists in Fixt
                    #if the dif. ratio between the two is above the thd
                    if ratio(base[afile][index], newbase[afile][index]) >= thd:
                        #and the localization is complete
                        if target[afile].get(index):
                            #the old content is copied (main goal)
                            newtarget[afile][index] = target[afile][index]
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

    return newtarget


#copies the dictionary's content into the .msg files inside dirpath
#this way we can keep comments and structure
def injector(loc, dirpath, encoding=None):

    line_p = re.compile(r'^[^\S\n]*\{([0-9]+)\}\{(?:.*)\}\{([^{]*)\}')
    startsWithBracket_p = re.compile(r'^[^\S\n]*\{')

    dirname = os.path.basename(dirpath)
    filepaths = common.pathfinder(dirpath)
    target_enc = common.encfinder(dirname)

    for filepath in filepaths:
        text_out = ''
        filename = os.path.split(filepath)[-1]
        lines = common.open2(filepath, encoding)
        for line in lines:
            if startsWithBracket_p.search(line):
                line_content = line_p.search(line)
                index = content.group(1)
                if (index in loc[filename]) and content.group(2):
                    line = line[:line_content.start(2)] + \
                           loc[filename][index] + \
                           line[line_content.end(2):]
                text_out += line
            else:
                text_out += line

        common.open2(filepath, target_enc, output=text_out)


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("base", default="ENGLISH_BASE",
                     help="English files used during the \
                     localization process (folder name)")
    par.add_argument("newbase", default="ENGLISH_FIXT",
                     help="Current English files (folder name)")
    par.add_argument("target", help="Target files (folder name)")
    par.add_argument("-t", "--threshold", type=float, default=1,
                     help="Lower similarity ratio threshold")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    for folder in (args.base, args.newbase):
        if not os.path.isdir(folder):
            sys.exit("\n{} folder missing. Aborting...".format(folder))

    target_new = args.target + '_NEW'
    if os.path.isdir(target_new):
        shutil.rmtree(target_new)

    base_enc = common.encfinder(args.base)
    target_enc = common.encfinder(args.target)
    output_path = os.path.join('.', target_new)

    print("\n\nWORKING...\n\n")

    base_loc = analyzer(args.base, base_enc, args.clearcache)
    base_loc_new = analyzer(args.newbase, base_enc, args.clearcache)
    target_loc = analyzer(args.target, target_enc, args.clearcache)

    target_loc_new = comparator(base_loc, base_loc_new,
                                target_loc, args.threshold)

    shutil.copytree(args.newbase, output_path)
    injector(target_loc_new, output_path, base_enc)

    print("\n\nALL DONE!\n\n")
    sys.exit()
