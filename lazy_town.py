"""Makes the target localization files compatible with the latest Fixt update,
the result will be a mixture of English and the target language. Levenshtein
algorithm is used (if you don't have python-Levenshtein, difflib will be used,
and its results tend to be very different). You can change the default
threshold of 1 (lower similarity ratio). At a value of 1, it would only copie
lines that haven't changed. You could use a slightly lower value to retain
lines with negligible changes. Creates a log of missing files and lines."""
import os, sys, copy, shutil, argparse
from os.path import join, isdir, abspath, splitext, basename
import common
from lang import Lang
try:
    from Levenshtein import ratio
except ImportError:
    import difflib
    def ratio(string1, string2):
        return difflib.SequenceMatcher(None, string1, string2).ratio()
    print("** python-Levenshtein module not found, using difflib instead **")

#updates target's files to match the file structure and naming on Fixt
#(files were merged and some filenames were changed)
def updater(base, base2, target, thd):

    renamed_lib = {'assblow':['kalnor'],   'bosasis':['bosasist'],
                   'boslori':['boslorri'], 'bvlad':  ['bv2vault'],
                   'lorri':  ['lorraine'], 'blade':  ['inblade'],
                   'trait':    ['trait - original descriptions',
                                'trait - sduibek detailed descriptions'],
                   'pro_misc': ['pro_misc - original exit grids',
                                'pro_misc - sduibek exit grids'],
                   'perk':     ['perk - original addiction titles',
                                'perk - sduibek addictions titles'],
                   'editor':   ['editor - original addiction titles',
                                'editor - sduibek addiction titles']}

    for lang in (base, target):
        for filename, filenames_new in renamed_lib.items():
            for filename_new in filenames_new:
                if (filename in lang) and (not filename_new in lang):
                    lang[filename_new] = lang[filename]
                    lang.filepaths[filename_new] = None
            lang.pop(filename, None)
            lang.filepaths.pop(filename, None)



    merged_lib = {'cow':'brahmin', 'demodog': 'alldogs', 'dog2': 'alldogs',
                  'dogmeat': 'alldogs', 'junkdog': 'alldogs',
                  'genlock':'locker', 'hhooker': 'hhookera'}

    #incase the files already exist and to make space for the changes
    for filename, filename_new in list(merged_lib.items()):
        if (filename not in base) or (filename_new in base):
            merged_lib.pop(filename)
        base.purge_with(target, limiter=filename)

    #compares the lines of the files listed in moved_lib
    for filename, filename_new in merged_lib.items():
        base.setdefault(filename_new, {})
        target.setdefault(filename_new, {})
        for index, line in list(base[filename].items()):
            for index_new, line_new in list(base2[filename_new].items()):
                if ratio(line, line_new) >= thd:
                    base[filename_new][index_new] = line
                    target[filename_new][index_new] = target[filename][index]

#base: English files used during the localization process of target
#base2: current English files
#target: localization files to update
#merges base2 and target by comparing base and base2, if the two lines have
#a similarity ratio higher than the threshold value, the target content is used
def comparator(base, base2, target, thd=1):
    target2 = copy.deepcopy(base2)
    target2.encoding = target.encoding
    base2.purge_with(base) #lines that were deleted or moved
    target.purge_with(base) #in case the localization is incomplete
    base.purge_with(base2, target) #to satisfy the above

    target2.flags = 0
    for filename in base:
        for index in base[filename]:
            if ratio(base[filename][index], base2[filename][index]) >= thd:
                if target[filename][index]: #in case the line is empty
                    target2[filename][index] = target[filename][index]
                    target2.flags += 1
    return target2

#copies lang's content into the .MSG files inside dirpath
#this way we can keep comments and structure
def injector(lang, dirpath, base_encoding):
    target_enc = lang.encoding
    filepaths = common.pathfinder(dirpath)
    for filepath in filepaths:
        text_out = ''
        filename = splitext(basename(filepath))[0].lower()
        lines = common.readlines(filepath, base_encoding)
        for line in lines:
            if Lang.line_pattern.search(line):
                line_sections = Lang.line_pattern.search(line)
                index = int(line_sections.group(1))
                if (index in lang[filename]) and line_sections.group(2):
                    line = (line[:line_sections.start(2)] +
                            str(lang[filename][index])    +
                            line[line_sections.end(2):])
                text_out += line
            else:
                text_out += line
        common.writelines(filepath, target_enc, text_out)


if __name__ == '__main__':

    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("base", default="ENGLISH_BASE",
                     help="Base English files")
    par.add_argument("base2", default="ENGLISH_FIXT",
                     help="Current English files")
    par.add_argument("target",
                     help="Target files")
    par.add_argument("-t", "--threshold", type=float, default=1,
                     help="Lower similarity ratio threshold")
    par.add_argument("-c", "--clearcache", action="store_true",
                     help="Clears json cache files")
    args = par.parse_args()

    target2_path =  join('.', basename(args.target) + '_LAZY_UPDATE')
    if isdir(target2_path):
        shutil.rmtree(target2_path)

    print("\nWORKING...\n")
    os.makedirs(Lang.cacheroot, exist_ok=True)

    base = Lang(abspath(args.base), args.clearcache)
    base2 = Lang(abspath(args.base2), args.clearcache)
    target = Lang(abspath(args.target), args.clearcache)

    t_size = target.size(False)
    b2_size = base2.size(False)

    updater(base, base2, target, args.threshold)

    shutil.copytree(args.base2, target2_path)
    target2 = comparator(base, base2, target, args.threshold)
    flags = target2.flags

    with open('lt-log-{}.txt'.format(target.dirname), 'w') as flog:
        log = "*"*31 + "\n"
        log += "{:^31}\n".format("GENERAL LOG")
        log += "*"*31 + "\n\n"

        log += "* {} version: \n".format(target.dirname.capitalize())
        log += "* English base version:\n"
        log += "* English Fixt version:\n\n"

        log += "* Similarity ratio threshold: {:.2f}\n\n".format(args.threshold)

        log += "* Comments:\n\n"

        log += "* {} of {} ({}%) {} lines were used.\n".format(
        flags, t_size, int(flags/t_size * 100), target.dirname.capitalize())
        log += "* {} of {} ({}%) lines remain in English.".format(
        b2_size-flags, b2_size, int((b2_size-flags)/b2_size * 100))

        log += "\n\n\n" + "*"*31 + "\n"
        log += "{:^31}\n".format("MISSING FILES AND INDICES LOG")
        log += "*"*31

        for lang in (base, base2, target):
            for lang_name in sorted(lang.purged):
                log += "\n\n\nPresent in {}".format(lang_name)
                log += " but not in {}\n".format(lang.dirname)
                for filename in sorted(lang.purged[lang_name]):
                    log += "\n{:<12.12} | ".format(filename)
                    for index in sorted(lang.purged[lang_name][filename]):
                        log += " {}".format(index)
        flog.write(log)

    injector(target2, target2_path, base2.encoding)
    print("\nALL DONE!\n")
    sys.exit()
