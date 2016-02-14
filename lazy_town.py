import os, re, ujson, shutil, argparse
from common import *

try:
    import Levenshtein
    isLevenshtein = True
except ImportError:
    import difflib
    print("Levenshtein module not found, using difflib instead")
    isLevenshtein = False

try:
    import ujson
    isUltra = True
except ImportError:
    import json
    print("ujson module not found, using json instead")
    isUltra = False


#makes a dictionary with the content of .msg files found in a given directory
#dictionary structure: {'filename':{'index':'line content'}}
def analyzer(directory, enc = None, clearcache = False):

    if not os.path.isfile('%s.json' % directory) or clearcache:
        data = {}
        thefiles = pathfinder(target = os.path.join('.', directory))

        for afile in thefiles:
            filename = os.path.split(afile)[-1]
            data[filename] = {}

            opt = [enc, None] #opt = [enconding, errors]
            lines = alt_read(afile, opt)

            for line in lines:
                if line.startswith('{'):
                    content = re.findall(r'^[ ]*\{([0-9]+)\}\{(.*)\}\{([^{]*)\}', line)
                    try:
                        index = content[0][0]
                        data[filename][index] = content[0][2]
                    except IndexError:
                        print("There are syntax errors in %s:\n\n" % afile)
                        print("Line content: '%s'\n\n" % line)
                        sys.exit("Aborting...")

        with open('%s.json' % directory, 'w') as cacheOut:
            if isUltra: ujson.dump(data, cacheOut)
            else: json.dump(data, cacheOut)

    else:
        with open('%s.json' % directory, 'r') as cacheIn:
            if isUltra: ujson.dump(data, cacheIn)
            else: json.dump(data, cacheIn)
    return data


#base => English files used during the localization process
#newbase => current English files
#target => localization files
#merges newbase and target by comparing base and newbase, if the two lines have
#a similarity ratio higher than the threshold value, the target content is used
def comparator(base, newbase, target, thd = 0.9):

    above_thd = 0
    below_thd = 0
    not_found = 0
    missing_files = 0
    log = ""

    if isLevenshtein:
        ratio = lambda x, y: Levenshtein.ratio(x, y)
    else:
        ratio = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()

    newtarget = newbase

    for afile in base.keys(): #for every filename in base (original english files)
        if newbase.get(afile): #only if it exists in newbase (Fixt's english files)
            if target.get(afile): #and only if it exists in target
                for index in base[afile].keys(): #for every index in filename
                    if newbase[afile].get(index): #only if line exists in Fixt's file
                        #if the difference ratio between the 2 strings is above the thd
                        if ratio(base[afile].get(index), newbase[afile].get(index)) >= thd:
                            if target[afile].get(index): #and the loc wasn't complete (?)
                                #the old content is copied
                                newtarget[afile][index] = target[afile][index]
                                above_thd += 1
                            else:
                                log += "Content not found in target (%s %s)\n" % (afile, index)
                                not_found += 1
                        else:
                            below_thd += 1
            else:
                log += "Missing file in target folder (%s)\n" % afile
                missing_files += 1
        else:
            log += "Missing file in Fixt folder (%s)\n" % afile
            missing_files += 1

    print("There were %i lines above the threshold" % above_thd)
    print("There were %i lines below the threshold" % below_thd)
    print("There are %i lines missing." % not_found)
    print("There are %i files missing" % missing_files)

    with open('lt-log.txt', 'w') as logfile:
        logfile.write(log)

    return newtarget


#copies the dictionary's content into the .msg files inside directory
def injector(loc, directory, enc = None):

    thefiles = pathfinder(target = os.path.join('.', directory))
    target_enc = encfinder(directory)

    for afile in thefiles:

        fileout_text = ''

        filename = os.path.split(afile)[-1]

        opt = [enc, None] #opt = [enconding, errors]
        lines = alt_read(afile, opt)

        for line in lines:

            if line.startswith('{'):
                content = re.search(r'^[ ]*\{([0-9]+)\}\{(.*)\}\{([^{]*)\}', line)
                index = content.group(1)
                if index in loc[filename]:
                    if content.group(3):
                        line = line[:content.start(3)] + loc[filename][index] + line[content.end(3):]
                fileout_text = fileout_text + line

            elif line == '\n':
                fileout_text = fileout_text + '\n'

            else:
                fileout_text = fileout_text + line

        err = None
        while True:
            fileout = open(afile, 'w', encoding = target_enc, errors = err)
            try:
                fileout.write(fileout_text)
                err = None
                break

            except UnicodeEncodeError:
                err = 'ignore'
                print(afile + "\n ---> Decoding error (using %s; information will be lost)\n" % target_enc)

            fileout.close()


if __name__ == '__main__':

    par = argparse.ArgumentParser(description="Makes the target localization \
    files compatible with the latest Fixt update, the result will be a \
    mixture of English and the target language. Levenshtein algorithm is used \
    (if you don't have python-Levenshtein, difflib will be used, and its \
    results tend to be very different), you can change the lower similarity \
    ratio threshold. Creates a log of missing files and lines.")
    par.add_argument("base", default="ENGLISH_BASE",
                     help="English files used during the localization process (folder name)")
    par.add_argument("newbase", default="ENGLISH_NEW", help="Current English files (folder name)")
    par.add_argument("target", help="Target files (folder name)")
    par.add_argument("-t", "--threshold", type=float, default=0.9, help="Lower similarity ratio threshold")
    par.add_argument("-c", "--clearcache", action="store_true", help="Clears json cache files")
    args = par.parse_args()

    thefiles = pathfinder()
    if not thefiles:
        sys.exit("There are no .msg files.")

    for folder in (args.base, args.newbase):
        if not os.path.isdir(folder):
            sys.exit("\n%s folder missing. Aborting..." % folder)

    target_new = args.target + '_NEW'
    if os.path.isdir(target_new):
        shutil.rmtree(target_new)

    base_enc = encfinder(args.base)
    target_enc = encfinder(args.target)
    output_path = os.path.join('.', target_new)

    print("\n\nWORKING...\n\n")

    base_dict = analyzer(args.base, base_enc, args.clearcache)
    new_base_dict = analyzer(args.newbase, base_enc, args.clearcache)
    target_dict = analyzer(args.target, target_enc, args.clearcache)

    target_new_dict = comparator(base_dict, new_base_dict, target_dict, args.threshold)

    shutil.copytree(args.newbase, output_path)
    injector(target_new_dict, output_path, base_enc)

    print("\n\nALL DONE!\n\n")
    sys.exit()
