import os, re, shutil

from main import *


def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'):
        pass
    else:
        exit()


def analyzer(dic, directory, enc = None):

    thefiles = pathfinder(target = os.path.join('.', directory))

    print(enc)
    print(directory)

    for afile in thefiles:
        filename = os.path.split(afile)[-1]
        dic[directory][filename] = {}

        par = [enc, None] #parameters = [enconding, errors]
        lines = alt_read(afile, par)

        for line in lines:
            if line.startswith('{'):
                content = re.findall(r'\{([0-9]+)\}\{(.*)\}\{([^{]*)\}', line)
                index = content[0][0]
                print('=A= =' + directory + '= =' + filename + '= =' + index + '=')
                dic[directory][filename][index] = content[0][2]


def replacer(dic, directory, enc = None):

    thefiles = pathfinder(target = os.path.join('.', directory))

    for afile in thefiles:

        fileout_text = ''

        filename = os.path.split(afile)[-1]

        par = [enc, None] #parameters = [enconding, errors]
        lines = alt_read(afile, par)

        for line in lines:
            if not dic[directory[:-4]].get(filename):
                fileout_text = fileout_text + line

            elif line.startswith('{'):
                content = re.search(r'[ ]*\{([0-9]+)\}\{(.*)\}\{([^{]*)\}', line)
                index = content.group(1)
                print('=R= =' + directory + '= =' + filename + '= =' + index + '=')
                if index in dic[directory[:-4]][filename]:
                    if content.group(3):
                        line = line[:content.start(3)] + dic[directory[:-4]][filename][index] + line[content.end(3):]
                fileout_text = fileout_text + line

            elif line == '\n' or '\r' or '\r\n':
                fileout_text = fileout_text + '\n'

            else:
                fileout_text = fileout_text + line

        with open(afile, 'w', encoding = enc) as fileout:
            fileout.write(fileout_text)


if __name__ == '__main__':

    start_msg = "\n\
lazy_updater.\n\
\n\n\
[y]es and hit enter to proceed or anything else to quit: "

    no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"

    """
    'rename'

    'ASSBLOW':'KALNOR'
    'BOSASIS':'BOSASIST'
    'BOSLORI':'BOSLORRI'

    'contents are now in'

    'BLADE':'INBLADE'
    'BVLAD':'BV2VAULT'
    'COW':'BRAHMIN'
    'DARL':'DARREL'
    'DEMOCOMP':'DEADCOMP'
    'DEMODOG':'ALLDOGS'
    'DOG2':'ALLDOGS'
    'DOGMEAT':'ALLDOGS'
    'GENGHOUL':'HOTGHOUL'
    'GENLOCK':'LOCKER'
    'GHOUL':'MANAGER'
    'HHOOKER':'HHOOKERA'
    'JER':'JEREM'
    'JUNKDOG':'ALLDOGS'
    """



    thefiles = pathfinder(excluded = ['__pycache__'])

    if thefiles:
        startcheck(start_msg)
    else:
        print(no_files_msg)
        input()
        exit()

    print ("\n\nWORKING...\n\n")

    data = {}
    dirnames = listdirs()
    basedir = 'ENGLISH'
    output = 'lu-output'
    dirnames.remove(basedir)

    for dirname in dirnames:
        output_path = os.path.join('.', output, dirname)
        enc = encfinder(dirname)
        data[dirname] = {}
        analyzer(data, dirname, enc)
        if os.path.isdir(output_path): shutil.rmtree(output_path)
        shutil.copytree(basedir, output_path)
        replacer(data, output_path, enc)


    input()
