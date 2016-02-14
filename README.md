# fallout-text-tools

A few scripts to ease the maintenance of Fallout's text files (1 and 2).
Made for both practical (Fallout Fixt) and educational purposes (aka ugly code).
Made for Python 3 in Windows (may not work on UNIX systems because of the way
I chose to handle file paths).


## Basic instructions for Windows

You'll need to install version 3.5 (or higher) of Python.
Download here: http://www.python.org/download/

Although they are optional, you should also install both ```python-Levenshtein```
and ```ujson```. You can do this via cmd with the following lines:
```
pip install python-Levenshtein
pip install ujson
```


## General instructions

If the files don't have a correct syntax everything will most likely explode, so
a good practice would be to run syntax_checker every time you make a change on
the files. Every script now uses a command-line interface.


## Scripts

### duplicate_checker.py
checks for duplicate index numbers, which usually equates to content been
override and not used

### linebreak_remover.py
removes line breaks, essential for the syntax_checker

### syntax_checker.py
spots ugly crash-inducing bugs

### lazy_town.py
makes unmantained localizations usable by "injecting" the new content in English

### mismatch_finder.py
looks for lines that should be same but aren't (translators fault)

### similarity_finder.py
ongoing project for creating a usable database of lines based on their
similarity ratio (Levenshtein distance). This would speed the localization
process in the future and could work as a loose mismatch_finder.py

### merger.py (outdated; do not use)
merges all files into a big one, for mass spell checking
