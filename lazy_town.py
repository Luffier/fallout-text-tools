"""Makes the target localization files compatible with the latest Fixt update,
the result will be a mixture of English and the target language. Levenshtein
algorithm is used (if you don't have python-Levenshtein, difflib will be used,
and its results tend to be very different). You can change the default
threshold of 1 (lower similarity ratio). At a value of 1, it would only copie
lines that haven't changed. You could use  a slightly lower value to retain
lines with negligible changes. Creates a log of missing files and lines."""
import os, sys, copy, shutil, argparse
from os.path import join, isdir, abspath, splitext, basename
import common
from lang import Lang
try:
    import Levenshtein
    def ratio(string1, string2):
        return Levenshtein.ratio(string1, string2)
except ImportError:
    import difflib
    def ratio(string1, string2):
        return difflib.SequenceMatcher(None, string1, string2).ratio()
    print("** python-Levenshtein module not found, using difflib instead **")


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

    for filename in base:
        for index in base[filename]:
            if ratio(base[filename][index], base2[filename][index]) >= thd:
                if target[filename][index]: #in case the line is empty
                    target2[filename][index] = target[filename][index]
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
                    line = (line[:line_sections.start(2)]   +
                            str(lang[filename][index])  +
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

    target2_path =  join('.', basename(args.target) + '_NEW')
    if isdir(target2_path):
        shutil.rmtree(target2_path)

    print("\nWORKING...\n")
    os.makedirs(Lang.cacheroot, exist_ok=True)

    base = Lang(abspath(args.base), args.clearcache)
    base2 = Lang(abspath(args.base2), args.clearcache)
    target = Lang(abspath(args.target), args.clearcache)

    shutil.copytree(args.base2, target2_path)
    target2 = comparator(base, base2, target, args.threshold)

    with open('lt-log.txt', 'w') as flog:
        log = "MISSING FILES AND INDICES LOG"
        for lang in (base2, target):
            for lang_name in lang.purged:
                log += "\n\n\nPresent in {}".format(lang_name)
                log += " but not in {}\n".format(lang.dirname)
                for filename in lang.purged[lang_name]:
                    log += "\n{:<12.12} | ".format(filename)
                    for index in lang.purged[lang_name][filename]:
                        log += " {}".format(index)
        flog.write(log)

    injector(target2, target2_path, base2.encoding)
    print("\nALL DONE!\n")
    sys.exit()
