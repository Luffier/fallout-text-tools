import os, fnmatch


def pathfinder(target = '.', excludedirs = []):
    filespaths = []
    for root, dirnames, filenames in os.walk(target):
        if excludedirs:
            for exclusion in excludedirs:
                if exclusion in dirnames:
                    dirnames.remove(exclusion)

        for filename in fnmatch.filter(filenames, '*.msg'):
            filespaths.append(os.path.join(root, filename))

    return filespaths


def encfinder(dirname):

    encoding_dic = {'latin1':['afrikaans', 'basque', 'catalan', 'danish', 'dutch',
    'english', 'faeroese', 'finnish', 'french', 'galician', 'german', 'icelandic',
    'irish', 'italian', 'norwegian', 'portuguese', 'spanish', 'swedish', 'english'],
    'latin2':['german', 'hungarian', 'romanian', 'croatian', 'slovak', 'slovene'],
    'cyrilic':['byelorussian', 'macedonian', 'serbian', 'ukrainian'],
    'cp866':['russian_fargus'], 'cp1251':['russian_1c'], 'cp1250':['czech', 'polish'],
    'gb18030':['chinese']}

    enc = ''

    for enconding in encoding_dic.keys():
        if any(dirname.lower() in language for language in encoding_dic[enconding]):
            enc = enconding
            break
        if not enc:
            enc = None
    return enc


#creates a tree of folders inside the output_root path based on a list of files
def treecreator(files, output_root):

    if not os.path.exists(output_root):
        os.makedirs(output_root)

    for afile in files:

        fullpath = os.path.dirname(afile)
        dirpath = os.path.join('.', output_root, fullpath[2:])

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)


def listdirs(target = '.', excluded = []):
    dirnames = []
    for dirname in os.listdir(target):
        if os.path.isdir(dirname):
            dirnames.append(dirname)
    for dirname in excluded:
        if dirname in dirnames:
            dirnames.remove(dirname)
    return dirnames


if __name__ == '__main__':

    input("Don't use this module")
    exit()
