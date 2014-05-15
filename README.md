fallout-text-tools
==================

A few scripts to ease the maintenance of Fallout's text files (1 and 2). Made for both practical and educational purposes (aka ugly code).
Made for Python 3.

All scripts have instructons. Just try them up.


==================
Basic instructions
==================

To run this script you'll need to install version 3 of Python.
Download: http://www.python.org/download/

Then, associate the .py file with Python (python.exe, located wherever you installed it).
Then execute the .py file just by double clicking on it, and now a new window asking 
for input should appear.

Just put the script along with the .msg files (or folders containing them) and run it. 

So, for a real example: put all the .py files inside ENGLISH, run one them, follow the instructions from the prompt, and see the magic.

====================
General instructions
====================

The results of duplicate_checker won't be good if the files don't have a correct syntax.
So a good order to run the scripts would be: 

linebreak_remover -----> syntax_checker -----> duplicate_checker

You can use chain.py to do exactly this.







====================
chain.py
====================
Runs the other scripts (except merger.py) in a given order to ease the process.



====================
duplicate_checker.py
====================
Gives you a text file with a log of all duplicate lines so you can manually remove them.



====================
linebreak_remover.py
====================
Gives you a folder (with the same directory structure) with all line breaks and unnecessary spaces remove from them.


Details:
    - Due to the layout of deadcomp.msg and fke_dude.msg, these files are skipped by default.



=================
syntax_checker.py
=================
Gives you a text file with a log of all syntax errors (missing brackets) so you can manually fix them.



=========
merger.py
=========
Merges all files into a big one.


Details:
    - You have some options on how the merged text is formatted. Example:


       """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
       "                                                                                  "
       " HEADER (OPTIONAL)                                                                "
       "                                                                                  "
       " FILENAME (OPTIONAL) INDEX NUMBER (OPTIONAL) TEXT                                 "
       "                                                                                  "
       " FOOTER (OPTIONAL)                                                                "
       "                                                                                  "
       """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""




       """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
       "                                                                                  "
       " ========================================                                         "
       " ========LOREMIPSUM.MSG  BEGINS==========                                         "
       " ========================================                                         "
       "                                                                                  "
       "                                                                                  "
       "                                                                                  "
       " LOREMIPSUM 100 Lorem ipsum dolor sit amet, consectetur adipiscing elit.          "
       " LOREMIPSUM 101 Cras eu lorem turpis.                                             "
       "                                                                                  "
       "                                                                                  "
       "                                                                                  "
       " ========================================                                         "
       " ========LOREMIPSUM.MSG  ENDS============                                         "
       " ========================================                                         "
       "                                                                                  "
       """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""