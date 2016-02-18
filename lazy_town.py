"""Makes the target localization files compatible with the latest Fixt update,
the result will be a mixture of English and the target language. Levenshtein
algorithm is used (if you don't have python-Levenshtein, difflib will be used,
and its results tend to be very different), you can change the lower similarity
ratio threshold. Creates a log of missing files and lines."""
import os, re, shutil, argparse
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


#makes a dictionary with the content of .msg files found in a given directory
#dictionary structure: {'filename': {'index': 'line content'}}
def analyzer(directory, enc=None, clearcache=False):

    if not os.path.isfile('{}.json'.format(directory)) or clearcache:
        data = {}
        thefiles = common.pathfinder(target=os.path.join('.', directory))

        for afile in thefiles:
            filename = os.path.split(afile)[-1]
            data[filename] = {}

            lines = common.open(afile, encoding=enc)

            for line in lines:
                if line.startswith('{'):
                    content = re.findall(r'^[ ]*\{([0-9]+)\}'
                                         r'\{(.*)\}'
                                         r'\{([^{]*)\}', line)
                    try:
                        index = content[0][0]
                        data[filename][index] = content[0][2]
                    except IndexError:
                        print("There are syntax errors in:\n{}".format(afile))
                        print("Line content: '{}'".format(line))
                        sys.exit("Aborting...")

        with open('{}.json'.format(directory), 'w') as cacheout:
            try:
                ujson.dump(data, cacheout)
            except NameError:
                json.dump(data, cacheout)

    else:
        with open('{}.json'.format(directory)) as cachein:
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
        if newbase.get(afile): #only if it exists in newbase (Fixt files)
            if target.get(afile): #and only if it exists in target (loc files)
                for index in base[afile]: #for every index in filename
                    if newbase[afile].get(index): #only if line exists in Fixt
                        #if the dif. ratio between the two is above the thd
                        if ratio(base[afile].get(index),
                                 newbase[afile].get(index)) >= thd:
                            #and the loc wasn't complete (?)
                            if target[afile].get(index):
                                #the old content is copied
                                newtarget[afile][index] = target[afile][index]
                                above_thd += 1
                            else:
                                log += "Content not found in target "
                                log += "({} {})\n".format(afile, index)
                                not_found += 1
                        else:
                            below_thd += 1
            else:
                log += "Missing file in target folder ({})\n".format(afile)
                missing_files += 1
        else:
            log += "Missing file in Fixt folder ({})\n".format(afile)
            missing_files += 1

    print("There were {:d} lines above the threshold".format(above_thd))
    print("There were {:d} lines below the threshold".format(below_thd))
    print("There are {:d} lines missing.".format(not_found))
    print("There are {:d} files missing".format(missing_files))

    with open('lt-log.txt', 'w') as logfile:
        logfile.write(log)

    return newtarget


#copies the dictionary's content into the .msg files inside directory
def injector(loc, directory, enc=None):

    thefiles = common.pathfinder(target=os.path.join('.', directory))
    target_enc = common.encfinder(directory)

    for afile in thefiles:

        text_out = ''

        filename = os.path.split(afile)[-1]

        lines = common.open(afile, encoding=enc)

        for line in lines:

            if line.startswith('{'):
                content = re.search(r'^[ ]*\{([0-9]+)\}'
                                    r'\{(.*)\}'
                                    r'\{([^{]*)\}', line)
                index = content.group(1)
                if index in loc[filename]:
                    if content.group(3):
                        line = line[:content.start(3)] + \
                               loc[filename][index] + \
                               line[content.end(3):]
                text_out += line

            elif line == '\n':
                text_out += '\n'

            else:
                text_out += line

        common.open(afile, out=text_out, encoding=target_enc, errors=err)


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("base", default="ENGLISH_BASE",
                     help="English files used during the \
                     localization process (folder name)")
    par.add_argument("newbase", default="ENGLISH_NEW",
                     help="Current English files (folder name)")
    par.add_argument("target", help="Target files (folder name)")
    par.add_argument("-t", "--threshold", type=float, default=0.9,
                     help="Lower similarity ratio threshold")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    thefiles = common.pathfinder()
    if not thefiles:
        sys.exit("There are no .msg files.")

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

    base_dict = analyzer(args.base, base_enc, args.clearcache)
    new_base_dict = analyzer(args.newbase, base_enc, args.clearcache)
    target_dict = analyzer(args.target, target_enc, args.clearcache)

    target_new_dict = comparator(base_dict, new_base_dict,
                                 target_dict, args.threshold)

    shutil.copytree(args.newbase, output_path)
    injector(target_new_dict, output_path, base_enc)

    print("\n\nALL DONE!\n\n")
    sys.exit()
