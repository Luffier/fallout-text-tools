import os, fnmatch


#returns a list of the folder names in target minus excluded (list of folders)
#excludes folders with no .msg files (recursive)
def listdirs(target = '.', excluded = []):
    dirnames = [dirname for dirname in os.listdir(target) if os.path.isdir(dirname)]
    dirnames = [dirname for dirname in dirnames if dirname not in excluded]

    for dirname in dirnames:
        flag = False
        for root, dirs, files in os.walk(dirname):
            if fnmatch.filter(files, '*.msg'):
                flag = True
                break
        if not flag:
            dirnames.remove(dirname)

    return dirnames


#returns a list of the files (absolute path) in a target folder minus excluded (list of folder names)
def pathfinder(target = '.', excluded = []):
    filespaths = []
    for root, dirnames, filenames in os.walk(target):
        if excluded:
            for exclusion in excluded:
                if exclusion in dirnames:
                    dirnames.remove(exclusion)
        for filename in fnmatch.filter(filenames, '*.msg'):
            filespaths.append(os.path.join(root, filename))
    return filespaths


#returns the encoding of a given folder name based on a dictionary on known
#languages and their encoding (not guessing involved)
def encfinder(dirname):

    codec_dic = {'cp1252':['english', 'french', 'german', 'italian', 'spanish'],
    'latin2':['hungarian'], 'cp866':['russian_fargus'], 'cp1251':['russian_1c'],
    'cp1250':['czech', 'polish'], 'gb18030':['chinese']}

    enc = None
    for codec in codec_dic.keys():
        if [lang for lang in codec_dic[codec] if lang in dirname.lower()]:
            enc = codec
            break
    return enc


#creates a tree of folders inside the target path based on a list of files
#this way we don't create unnecesary folders as we only work with .msg files
def treecreator(files, target):

    if not os.path.exists(target):
        os.makedirs(target)

    for afile in files:

        fullpath = os.path.dirname(afile)
        dirpath = os.path.join('.', target, fullpath[2:])

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)


#simple open -> readlines but with exceptions handling for either a unknown
#codec name/alias or a decoding error, where parameters = [enconding, errors]
def alt_read(filepath, parameters = [None, None]):
    while True:
        try:
            ofile = open(filepath, 'r', encoding=parameters[0], errors=parameters[1])
            try:
                content = ofile.readlines()
                break

            except UnicodeDecodeError:
                print(filepath + "\n ---> Decoding error (using %s) (ignoring for now; information will be lost)\n" % parameters[0])
                parameters[1] = 'ignore'

            ofile.close()

        except LookupError:
            parameters[0] = input(filepath + "\n ---> Unknown codec. Please type a supported codec: ")

    return content


if __name__ == '__main__':

    sys.exit("Don't use this module")
