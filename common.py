import os, sys, shutil, fnmatch
from os.path import basename

#returns a list of the folder names in the target path minus excluded and
#folders with no .MSG files down the directory tree
def listdirs(path='.', excluded=[]):
    excluded.append('__pycache__')
    thedirs = next(os.walk(path))[1] #os.walk() returns root, dirs [1], files
    thedirs = [adir for adir in thedirs if adir not in excluded]
    for adir in thedirs:
        for root, dirs, files in os.walk(adir):
            if fnmatch.filter(files, '*.MSG'):
                break
            else:
                thedirs.remove(adir)
    return thedirs

#returns a list of the files (absolute paths) in the target path that match
#the file_filter pattern and aren't in a excluded dir
def pathfinder(path='.', excluded=[], file_filter='*.MSG'):
    filespaths = []
    excluded.append('__pycache__')
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded]
        for afile in fnmatch.filter(files, file_filter):
            filespaths.append(os.path.join(root, afile))
    return filespaths

#returns the encoding of a given folder name based on a dictionary of known
#languages keywords and their respective encoding
def encfinder(dirname):
    encoding = None
    codec_lib = {
    'cp1252' : ['english', 'french', 'german', 'italian', 'spanish'],
    'latin2' : ['hungarian'],
    'cp866'  : ['russian_fargus'],
    'cp1251' : ['russian_1c'],
    'cp1250' : ['czech', 'polish'],
    'gb18030': ['chinese']}

    for codec, keywords in codec_lib.items():
        for keyword in keywords:
            if keyword in dirname.lower():
                encoding = codec
                break

    if not encoding:
        print("Couldn't find the codec for {}".format(dirname))
        encoding = input("Type a supported codec "
                         "(nothing for your system's default): ")
        if not encoding:
            encoding = None
    return encoding

#simple 'open and readlines' but with exception handling for decoding errors
def readlines(path, encoding):
    errors=None
    while True:
        with open(path, 'r', encoding=encoding, errors=errors) as thefile:
            try:
                lines = thefile.readlines()
                return lines
            except UnicodeDecodeError:
                print("Decoding error in {} ({}) (ignoring; information will "
                      "be lost)".format(basename(path), encoding))
                print("Fullpath: {}".format(path))
                errors = 'ignore'

#simple 'open and write' but with exception handling for encoding errors
def writelines(path, encoding, output):
    errors=None
    while True:
        with open(path, 'w', encoding=encoding, errors=errors) as thefile:
            try:
                thefile.write(output)
                break
            except UnicodeEncodeError:
                print("Encoding error in {} ({}) (ignoring; information will "
                      "be lost)".format(basename(path), encoding))
                print("Fullpath: {}".format(path))
                errors = 'ignore'

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
