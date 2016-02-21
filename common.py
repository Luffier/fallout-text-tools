import os, sys, shutil, fnmatch


#returns a list of the folder names in the target path minus excluded and
#folders with no .msg files down the directory tree
def listdirs(path='.', excluded=[]):
    excluded.append('__pycache__')
    thedirs = next(os.walk(path))[1] #os.walk() returns root, dirs [1], files
    thedirs = [adir for adir in thedirs if adir not in excluded]
    for adir in thedirs:
        for root, dirs, files in os.walk(adir):
            if fnmatch.filter(files, '*.msg'):
                break
            else:
                thedirs.remove(adir)
    return thedirs

#returns a list of the files (absolute paths) in the target path that match
#the file_filter pattern and aren't in a excluded dir
def pathfinder(path='.', excluded=[], file_filter='*.msg'):
    filespaths = []
    excluded.append('__pycache__')
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded]
        for afile in fnmatch.filter(files, file_filter):
            filespaths.append(os.path.join(root, afile))
    return filespaths

#returns the encoding of a given folder name based on a dictionary of known
#languages keywords and their respective encoding (not guessing involved)
def encfinder(dirname):
    encoding = None
    codec_dic = {
    'cp1252' : ['english', 'english_base', 'english_fixt', 'french', 'german',
                'italian','spanish', 'spanish_female', 'spanish_male'],
    'latin2' : ['hungarian'],
    'cp866'  : ['russian_fargus'],
    'cp1251' : ['russian_1c'],
    'cp1250' : ['czech', 'polish'],
    'gb18030': ['chinese']}
    for codec, lang_keyword in codec_dic.items():
        if dirname.lower() in lang_keyword:
            encoding = codec
            break
    return encoding

#simple 'open and readlines|write' but with exceptions handling for either an
#unknown codec name/alias or a decoding error
def open2(path, encoding=None, output=None):
    errors=None
    if output:
        mode = 'w'
    else:
        mode = 'r'
    while True:
        try:
            with open(path, mode, encoding=encoding, errors=errors) as thefile:
                try:
                    if output:
                        thefile.write(output)
                        break
                    else:
                        lines = thefile.readlines()
                        return lines
                except UnicodeDecodeError:
                    print(path)
                    print(" ---> Decoding error ({}) (ignoring for now; \
                          information will be lost)".format(encoding))
                    errors = 'ignore'
        except LookupError:
            print(path)
            encoding = input(" ---> Unknown codec. Type a supported codec \
                             (nothing for your system's default): ")
            if not encoding:
                encoding = None

#for copying files and creating dirs as needed
def copy(source, target):
    while True:
        try:
            shutil.copy(source, target)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            continue
        break


if __name__ == '__main__':

    sys.exit("Don't use this module as a standalone program")
