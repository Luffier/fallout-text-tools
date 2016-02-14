import os, sys, fnmatch


#returns a list of the folder names in target minus excluded (list of folders)
#excludes folders with no .msg files (recursive)
def listdirs(target = '.', excluded = ['__pycache__']):

    dirs = [adir for adir in os.listdir(target) if os.path.isdir(adir)]
    dirs = [adir for adir in dirs if adir not in excluded]

    for adir in dirs:
        flag = False
        for wroot, wdirs, wfiles in os.walk(adir):
            if fnmatch.filter(wfiles, '*.msg'):
                flag = True
                break
        if not flag:
            dirs.remove(adir)
    return dirs


#returns a list of the files (absolute path) in a
#target folder minus excluded (list of folders)
def pathfinder(target = '.', excluded = ['__pycache__']):

    filespaths = []
    for root, dirnames, filenames in os.walk(target):
        if excluded:
            for exclusion in excluded:
                if exclusion in dirnames:
                    dirnames.remove(exclusion)
        for filename in fnmatch.filter(filenames, '*.msg'):
            filespaths.append(os.path.join(root, filename))
    return filespaths


#returns the encoding of a given folder name based on a dictionary
#on known languages and their encoding (not guessing involved)
def encfinder(dirname):

    codec_dic = {
    'cp1252':['english', 'french', 'german', 'italian', 'spanish'],
    'latin2':['hungarian'],
    'cp866':['russian_fargus'],
    'cp1251':['russian_1c'],
    'cp1250':['czech', 'polish'],
    'gb18030':['chinese']
    }

    enc = None
    for codec in codec_dic.keys():
        if [lang for lang in codec_dic[codec] if lang in dirname.lower()]:
            enc = codec
            break
    return enc


#simple open -> readlines but with exceptions handling for either a unknown
#codec name/alias or a decoding error, where opt = [enconding, errors]
def alt_read(filepath, opt = [None, None]):

    while True:
        try:
            ofile = open(filepath, 'r', encoding=opt[0], errors=opt[1])
            try:
                content = ofile.readlines()
                break

            except UnicodeDecodeError:
                print(filepath + "\n ---> Decoding error (using %s) (ignoring \
                      for now; information will be lost)\n" % opt[0])
                opt[1] = 'ignore'

            ofile.close()

        except LookupError:
            opt[0] = input(filepath + "\n ---> Unknown codec. Please type a \
                           supported codec: ")

    return content


if __name__ == '__main__':

    sys.exit("Don't use this module")
