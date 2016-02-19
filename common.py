import os, sys, shutil, fnmatch


#returns a list of the folder names in the target path minus excluded and
#folders with no .msg files down the directory tree
def listdirs(target='.', excluded=[]):
    excluded.append('__pycache__')
    thedirs = next(os.walk(target))[1] #os.walk() returns root, dirs [1], files
    thedirs = [adir for adir in thedirs if adir not in excluded]
    for adir in thedirs:
        for root, dirs, files in os.walk(adir):
            if fnmatch.filter(files, '*.msg'):
                break
        else:
            thedirs.remove(adir)
    return thedirs

#returns a list of the files (absolute path) in the target path minus excluded
def pathfinder(target='.', excluded=[]):
    filespaths = []
    excluded.append('__pycache__')
    for root, dirs, files in os.walk(target, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded]
        for afile in fnmatch.filter(files, '*.msg'):
            filespaths.append(os.path.join(root, afile))
    return filespaths

#returns the encoding of a given folder name based on a dictionary of known
#languages keywords and their respective encoding (not guessing involved)
def encfinder(dirname):
    encoding = None
    codec_dic = {
    'cp1252': ['english', 'english_fixt', 'french', 'german', 'italian',
               'spanish', 'spanish_female', 'spanish_male'],
    'latin2': ['hungarian'],
    'cp866': ['russian_fargus'],
    'cp1251': ['russian_1c'],
    'cp1250': ['czech', 'polish'],
    'gb18030': ['chinese']
    }

    for codec, lang_keyword in codec_dic.items():
        if dirname.lower() in lang_keyword:
            encoding = codec
            break
    return encoding

#simple 'open and readlines|write' but with exceptions handling for either an
#unknown codec name/alias or a decoding error
def open2(filepath, out=None, encoding=None):
    err=None
    while True:
        try:
            with open(filepath, 'r', encoding=encoding, errors=err) as thefile:
                try:
                    if out:
                        thefile.write(out)
                    else:
                        lines = thefile.readlines()
                        return lines

                    break
                except UnicodeDecodeError:
                    print(filepath)
                    print(" ---> Decoding error (%s) (ignoring for now; \
                          information will be lost)" % encoding)
                    err = 'ignore'
        except LookupError:
            print(filepath)
            encoding = input(" ---> Unknown codec. Type a supported codec: ")
            if not encoding:
                encoding = None
    return lines

#for copying files and creating dirs as needed
def copy(source, destination):
    while True:
        try:
            shutil.copy(source, destination)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            continue
        break


if __name__ == '__main__':

    sys.exit("Don't use this module")
