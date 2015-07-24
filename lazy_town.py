import os, re, shutil, difflib

from main import *


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
                index = content[0][0]
                #print('=A= =' + filename + '= =' + index + '=')
                data[filename][index] = content[0][2]

    return data


def comparator(base, newbase, target):
    threshold = 0.90
    diff = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio() # :)
    newtarget = newbase
    for afile in base.keys(): #for every filename in base (original english files)
        if newbase.get(afile): #only if it exists in newbase (Fixt's english files)
            for index in base[afile].keys(): #for every index in filename
                if newbase[afile].get(index): #only if it exists in Fixt's file
                    #if the difference between the two strings are lower than the threshold
                    if diff( base[afile].get(index), newbase[afile].get(index) ) > threshold:
                        if target[afile].get(index): #in case the translation isn't complete?
                            newtarget[afile][index] = target[afile][index] #the old content is copied
                        else:
                            print('%s %s' % (afile, index))
    return newtarget




def injector(dic, directory, enc = None):

    thefiles = pathfinder(target = os.path.join('.', directory))
    out_enc = encfinder(directory)

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
            fileout = open(afile, 'w', encoding = out_enc, errors = err)
            try:
                fileout.write(fileout_text)
                err = None
                break

            except UnicodeEncodeError:
                err = 'ignore'
                print('ERRRRRROR %s' % filename)

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

    print ("\n\nWORKING...\n\n")


    english_base = 'ENGLISH'
    english_new = 'ENGLISH_FIXT'
    target_base = 'CZECH'
    target_new = 'CZECH_NEW'

    output = 'lu-output'

    output_path = os.path.join('.', output, target_new)

    enc = 'cp1252'
    english_base_dic = analyzer(english_base, enc)
    english_new_dic = analyzer(english_new, enc)
    enc = 'cp1250'
    target_base_dic = analyzer(target_base, enc)


    target_new_dic = comparator(english_base_dic, english_new_dic, target_base_dic)

    enc = 'cp1252'
    shutil.copytree(english_new, output_path)
    injector(target_new_dic, output_path, enc)


    input()
