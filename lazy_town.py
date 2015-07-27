import os, re, shutil

try:
    import Levenshtein
    isLevenshtein = True
except ImportError:
    import difflib
    print("Levenshtein module not found, using difflib instead")
    isLevenshtein = False

from common import *


#makes a dictionary with the content of .msg files found in a given directory
#dictionary structure: {'filename':{'index':'line content'}}
def analyzer(directory, enc = None):

    data = {}

    thefiles = pathfinder(target = os.path.join('.', directory))

    for afile in thefiles:
        filename = os.path.split(afile)[-1]
        data[filename] = {}

        par = [enc, None] #parameters = [enconding, errors]
        lines = alt_read(afile, par)

        for line in lines:
            if line.startswith('{'):
                content = re.findall(r'^[ ]*\{([0-9]+)\}\{(.*)\}\{([^{]*)\}', line)
                try:
                    index = content[0][0]
                    data[filename][index] = content[0][2]
                except IndexError:
                    input("There are syntax errors in %s:\n\nLine content: '%s'\n\nAborting..." % (afile, line))
                    exit()

    return data


#base => English files used during the localization process
#newbase => current English files
#target => localization files
#merges newbase and target by comparing base and newbase, if the two lines have
#a similarity ratio higher than the threshold value, the target content is used
def comparator(base, newbase, target, threshold = 0.9):

    above_threshold = 0
    below_threshold = 0
    not_found = 0

    if isLevenshtein:
        ratio = lambda x, y: Levenshtein.ratio(x, y)
    else:
        ratio = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()

    newtarget = newbase

    for afile in base.keys(): #for every filename in base (original english files)
        if newbase.get(afile): #only if it exists in newbase (Fixt's english files)
            for index in base[afile].keys(): #for every index in filename
                if newbase[afile].get(index): #only if it exists in Fixt's file
                    #if the difference ratio between the two strings is above the threshold
                    if ratio( base[afile].get(index), newbase[afile].get(index) ) >= threshold:
                        if target[afile].get(index): #and the translation wasn't complete (?)
                            newtarget[afile][index] = target[afile][index] #the old content is copied
                            above_threshold += 1
                        else:
                            print("Content not found in target (%s %s)" % (afile, index))
                            not_found += 1
                    else:
                        below_threshold += 1
    print("There were %i lines above the threshold, %i below and %i were missing." % (above_threshold, below_threshold, not_found))

    return newtarget


#copies the dictionary's content into the .msg files inside directory
def injector(dic, directory, enc = None):

    thefiles = pathfinder(target = os.path.join('.', directory))
    target_enc = encfinder(directory)

    for afile in thefiles:

        fileout_text = ''

        filename = os.path.split(afile)[-1]

        par = [enc, None] #parameters = [enconding, errors]
        lines = alt_read(afile, par)

        for line in lines:

            if line.startswith('{'):
                content = re.search(r'^[ ]*\{([0-9]+)\}\{(.*)\}\{([^{]*)\}', line)
                index = content.group(1)
                if index in dic[filename]:
                    if content.group(3):
                        line = line[:content.start(3)] + dic[filename][index] + line[content.end(3):]
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
                print(afile + "\n ---> Decoding error (using %s) (ignoring for now; information will be lost)\n" % target_enc)

            fileout.close()



if __name__ == '__main__':

    start_msg = "Using ENGLISH_BASE and ENGLISH_FIXT\n\
[y]es and hit enter to proceed or anything else to quit: "

    no_files_msg = "There are no .msg files"


    thefiles = pathfinder(excluded = ['__pycache__'])

    if thefiles:
        inputcheck = input(start_msg).lower()
        if inputcheck in ('yes','y'):
            pass
        else:
            exit()
    else:
        print(no_files_msg)
        input()
        exit()


    base = 'ENGLISH_BASE'
    base_new = 'ENGLISH_FIXT'
    if not os.path.isdir(base):
        input("\n%s folder missing. Aborting..." % base)
        exit()
    if not os.path.isdir(base_new):
        input("\n%s folder missing. Aborting..." % base_new)
        exit()

    dirnames = listdirs(excluded = [base, base_new])
    for i in range(len(dirnames)):
        print("%i) %s" % (i, dirnames[i]))

    target = dirnames[int(input("\nType the number of the language/folder to work with: "))]

    target_new = target + '_NEW'
    if os.path.isdir(target_new): shutil.rmtree(target_new)

    base_enc = encfinder(base)
    target_enc = encfinder(target)
    output_path = os.path.join('.', target_new)

    print("\n\nWORKING...\n\n")

    base_dic = analyzer(base, base_enc)
    base_new_dic = analyzer(base_new, base_enc)
    target_dic = analyzer(target, target_enc)

    target_new_dic = comparator(base_dic, base_new_dic, target_dic)

    shutil.copytree(base_new, output_path)
    injector(target_new_dic, output_path, base_enc)

    input("\n\nALL DONE!\n\n")
