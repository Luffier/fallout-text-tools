# fallout-text-tools

A few scripts to ease the maintenance of Fallout's text files (1 and 2).
Made for both practical (Fallout Fixt) and educational purposes (aka ugly code).
Made for Python 3 in Windows (may not work on UNIX systems because of the way
I choose to handle file paths).


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
### linebreak_remover.py
### syntax_checker.py
### lazy_town.py
### lazy_updater.py
### merger.py (Outdated; Do not use)
