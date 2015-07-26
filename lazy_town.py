import os, re, shutil

try:
    import Levenshtein
    isLevenshtein = True
except ImportError:
    import difflib
    isLevenshtein = False

from common import *


def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'):
        pass
    else:
        exit()


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
                    input("There are ")
                    exit()

    return data


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
                #print('=R= =' + filename + '= =' + index + '=')
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

    start_msg = "[y]es and hit enter to proceed or anything else to quit: "

    no_files_msg = "There are no .msg files"


    thefiles = pathfinder(excluded = ['__pycache__'])

    if thefiles:
        startcheck(start_msg)
    else:
        print(no_files_msg)
        input()
        exit()


    base = 'ENGLISH'
    base_new = 'ENGLISH_FIXT'
    target = input("\nType the name of the language/folder to work with: ")
    while not os.path.isdir(target):
        target = input("\nThe folder does not exist, try again: ")
    target_new = target + '_NEW'



    base_enc = encfinder(base)
    target_enc = encfinder(target)
    output_path = os.path.join('.', target_new)

    print ("\n\nWORKING...\n\n")

    base_dic = analyzer(base, base_enc)
    base_new_dic = analyzer(base_new, base_enc)
    target_dic = analyzer(target, target_enc)

    target_new_dic = comparator(base_dic, base_new_dic, target_dic)

    shutil.copytree(base_new, output_path)
    injector(target_new_dic, output_path, base_enc)


    input()
