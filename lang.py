import re, sys
from os import makedirs
from os.path import join, isdir, isfile, splitext, basename
from math import ceil
import common
try:
    import ujson as json
except ImportError:
    import json
    print("** ujson module not found, using json instead **")
try:
    from Levenshtein import ratio
except ImportError:
    import difflib
    def ratio(string1, string2):
        return difflib.SequenceMatcher(None, string1, string2).ratio()
    print("** python-Levenshtein module not found, using difflib instead **")

class Lang:

    line_pattern = re.compile(r'^[^\S\n]*\{([0-9]+)\}\{(?:.*)\}\{([^{]*)\}')
    cacheroot = join('.', 'ftt-cache')

    def __init__(self, dirpath, clearcache=False):
        self.dirpath = dirpath
        self.dirname = basename(self.dirpath)
        self.clearcache = clearcache
        self.encoding = common.encfinder(self.dirname)
        self.filepaths = self.getfilepaths()
        self.data = self.getdata()
        self.purged = {}

    def __getitem__(self, filename):
        return self.data[filename]

    def __setitem__(self, filename, value):
        self.data[filename] = value

    def __iter__(self):
        return iter(self.data)

    #number of files
    def __len__(self):
        return len(self.data)

    #number of lines (with or without empty lines)
    def size(self, complete=True):
        if complete:
            return sum(len(f) for f in self.data.values())
        else:
            return sum(1 for c in self.data.values() for l in c.values() if l)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def getline(self, filename, index):
        try:
            return self.data[filename][index]
        except KeyError:
            return None

    def pop(self, key, default=None):
        return self.data.pop(key, default)

    def setdefault(self, key, default=None):
        self.data.setdefault(key, default)

    #search result structure: ("filename", "index") or a list
    def search(self, line, first_match=True):
        search_result = []
        for filename in self.data:
            for index in self.data[filename]:
                if line == self.data[filename][index]:
                    if first_match:
                        return (filename, index)
                    else:
                        search_result.append((filename, index))
        return search_result

    #search result structure: {ratio: [("filename", "index")]}
    def search_similar(self, line, thd=0.5):
        search_result = {}
        for filename in self.data:
            for index in self.data[filename]:
                line_ratio = ratio(line, self.data[filename][index])
                if line_ratio >= thd:
                    line_ratio = round(line_ratio * 100)
                    search_result.setdefault(line_ratio, [])
                    search_result[line_ratio].append((filename, index))
        return search_result

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
            makedirs(Lang.cacheroot, exist_ok=True)
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

    #data structure: {"filename": {"index": "string"}}
    def parser(self, rawlines):
        lines = {}
        for rawline in rawlines:
            if Lang.line_pattern.search(rawline):
                try:
                    line_sections = Lang.line_pattern.search(rawline).groups()
                    index = line_sections[0]
                    content = line_sections[1]
                    lines[index] = content
                except (IndexError, AttributeError):
                    sys.exit("Syntax errors in:\n{}".format(self.filepath))
        return lines

    #global form structure: {"filename|index": "string"}
    def global_parser(self, complete=True):
        lines = {}
        for filename in self.data:
            for index in self.data[filename]:
                if complete or self.data[filename][index]:
                    lines[filename+'|'+ index] = self.data[filename][index]
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
                    self.filepaths.pop(filename)
                else:
                    for index in list(self.data[filename]):
                        if index not in lang[filename]:
                            self.purged[lang.dirname].setdefault(filename, [])
                            self.purged[lang.dirname][filename].append(index)
                            self.data[filename].pop(index)
        return self.purged
