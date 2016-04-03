# fallout-text-tools

A few scripts to ease the maintenance of Fallout's text files (1 and 2).
Made for both practical (Fallout Fixt) and educational purposes (ugly code and
lots of refactoring just for the sake of refactoring).
Made for Python 3 in Windows (but it should work on UNIX systems too).


## Basic instructions for Windows

You'll need to install version 3.5 (or higher) of Python.
Download here: http://www.python.org/download/

Although they are optional, you should also install both ```python-Levenshtein```
and ```ujson```. You can do this via ```cmd``` with the following lines:
```
pip install ujson python-Levenshtein
```

In case ```pip``` gives you an error (this usually means you don't have the
required compiler), you can use the binaries at:
http://www.lfd.uci.edu/~gohlke/pythonlibs/

For this, first upgrade pip:
```
python -m pip install --upgrade pip
```

And then use ```pip install``` followed by the ```.whl``` file path.



## General instructions

If the files don't have a correct syntax everything will most likely explode, so
a good practice would be to run syntax_checker every time you make a change on
the files.

Any module that uses lang.py (lazy_town, mismatch_finder and
similarity_finder) needs the files to be clear of line breaks (use
linebreak_remover with the parameter ```-e```).

Every script now uses a command-line interface.


## Scripts

### duplicate_checker.py
checks for duplicate index numbers, which usually equates to content been
override and not used

### linebreak_remover.py
removes line breaks, essential for the syntax_checker

### syntax_checker.py
spots ugly crash-inducing bugs

### lazy_town.py
makes unmaintained localizations usable by "injecting" good lines (based on
their similarity ratio -using Levenshtein distance-) into the Fixt files

### mismatch_finder.py
looks for lines that should be same but aren't (translators fault)

### similarity_finder.py
ongoing project for creating a usable database of lines based on their
similarity ratio. This would speed the localization process in the future and
could work as a kind of translation memory.
