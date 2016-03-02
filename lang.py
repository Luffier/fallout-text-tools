"""Makes the target localization files compatible with the latest Fixt update,
the result will be a mixture of English and the target language. Levenshtein
algorithm is used (if you don't have python-Levenshtein, difflib will be used,
and its results tend to be very different). You can change the default
threshold of 1 (lower similarity ratio). At a value of 1, it would only copie
lines that haven't changed. You could use  a slightly lower value to retain
lines with negligible changes. Creates a log of missing files and lines."""
import re, sys
from os.path import join, isdir, isfile, splitext, basename
from collections import namedtuple
import common
try:
    import ujson as json
except ImportError:
    import json
    print("** ujson module not found, using json instead **")


class Lang:

    line_pattern = re.compile(r'^[^\S\n]*\{([0-9]+)\}\{(?:.*)\}\{([^{]*)\}')
    id_pattern = re.compile(r'^(.+)\|([0-9]+)$')
    cacheroot = join('.', 'ftt-cache')

    def __init__(self, dirpath, clearcache=False):
        if not isdir(dirpath):
            raise ValueError("The directory doesn't exist")
        self.dirpath = dirpath
        self.dirname = basename(self.dirpath)
        self.clearcache = clearcache
        self.encoding = common.encfinder(self.dirname)
        self.filepaths = self.getfilepaths()
        if not self.filepaths:
            raise ValueError("There aren't any .MSG files")
        self.data = self.getdata()
        self.purged = {}

    def __getitem__(self, filename):
        return self.data[filename]

    def __setitem__(self, filename, value):
        self.data[filename] = value

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.filepaths)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def pop(self, key, default=None):
        return self.data.pop(key, default)

    #filepaths structure: {"filename": "filepath"}
    def getfilepaths(self):
        filepaths = {}
        for filepath in common.pathfinder(self.dirpath):
            filename = splitext(basename(filepath))[0]
            filepaths[filename.lower()] = filepath
        return filepaths

    #uses cache or parser() to get a nested dict with all the text data
    def getdata(self):
        cachepath = join(Lang.cacheroot, '{}.json'.format(self.dirname))
        if not isfile(cachepath) or self.clearcache:
            files = {}
            for filename, filepath in self.filepaths.items():
                rawlines = common.readlines(filepath, self.encoding)
                files[filename.lower()] = self.parser(rawlines)
            with open(cachepath, 'w') as cacheout:
                json.dump(files, cacheout)
            return files
        else:
            print("Using cached language data ({})".format(self.dirname))
            with open(cachepath, 'r') as cachein:
                return json.load(cachein)

    #data structure: {"filename": {index: "string"}}
    def parser(self, rawlines):
        lines = {}
        for rawline in rawlines:
            if Lang.line_pattern.search(rawline):
                try:
                    line_sections = Lang.line_pattern.search(rawline).groups()
                    index = int(line_sections[0])
                    content = line_sections[1]
                    lines[index] = content
                except (IndexError, AttributeError):
                    sys.exit("Syntax errors in:\n{}".format(self.filepath))
        return lines

    #global form structure: {"filename|index": "string"}
    def global_parser(self):
        lines = {}
        for filename in self.data:
            for index in self.data[filename]:
                lines[filename + "|" + str(index)] = self.data[filename][index]
        return lines

    #removes any filename and index not present in another Lang object
    #purged structure: {"lang dirname": {"filename": [indices]}}
    def purge_with(self, *args, limiter=[]):
        for lang in args:
            if type(lang) is not Lang:
                raise TypeError
            self.purged.setdefault(lang.dirname, {})
            filenames = list(self.data)
            if limiter:
                filenames = [f for f in list(self.data) if f in limiter]
            for filename in filenames:
                if filename not in lang:
                    self.purged[lang.dirname][filename] = ["*MISSING FILE*"]
                    self.data.pop(filename)
                else:
                    for index in list(self.data[filename]):
                        if index not in lang[filename]:
                            self.purged[lang.dirname].setdefault(filename, [])
                            self.purged[lang.dirname][filename].append(index)
                            self.data[filename].pop(index)
        return self.purged
