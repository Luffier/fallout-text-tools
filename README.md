# fallout-text-tools

A few scripts to ease the maintenance of Fallout's text files (1 and 2).
Made for both practical (Fallout Fixt) and educational purposes (aka ugly code).
Made for Python 3 in Windows.



## Basic instructions for Windows

You'll need to install version 3 of Python.
Download: http://www.python.org/download/




## General instructions

If the files don't have a correct syntax everything will most likely explode, so
a good practice would be to run syntax_checker every time you make a change on
the files.




## Scripts


### duplicate_checker.py

Creates a log of all duplicate lines so you can manually remove them.



### linebreak_remover.py

Removes unwanted line breaks and unnecessary spaces.
Outputs the files on a folder with the same directory structure.
* Due to the layout of deadcomp.msg, democomp.msg and fke_dude.msg, these files are skipped by default.



### syntax_checker.py

Creates a log of all syntax errors (missing brackets) so you can manually fix them.



### lazy_town.py

ENGLISH (BASE) ENGLISH_FIXT (NEW BASE)
LANGUAGE (TARGET) LANGUAGE_NEW (OUTPUT)



### lazy_updater.py



### chain.py (Outdated; Do not use)

Runs the other scripts (except merger.py) in a given order to ease the process.



### merger.py (Outdated; Do not use)

Merges all files into a big one.
* You have some options on how the merged text is formatted. Example:


```
|""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""|
|                                                                                  |
| HEADER (OPTIONAL)                                                                |
|                                                                                  |
| FILENAME (OPTIONAL) INDEX NUMBER (OPTIONAL) TEXT                                 |
|                                                                                  |
| FOOTER (OPTIONAL)                                                                |
|                                                                                  |
|""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""|
```

Or

```
|""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""|
|                                                                                  |
| ========================================                                         |
| ========LOREMIPSUM.MSG  BEGINS==========                                         |
| ========================================                                         |
|                                                                                  |
|                                                                                  |
|                                                                                  |
| LOREMIPSUM 100 Lorem ipsum dolor sit amet, consectetur adipiscing elit.          |
| LOREMIPSUM 101 Cras eu lorem turpis.                                             |
|                                                                                  |
|                                                                                  |
|                                                                                  |
| ========================================                                         |
| ========LOREMIPSUM.MSG  ENDS============                                         |
| ========================================                                         |
|                                                                                  |
|""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""|
```
