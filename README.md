fallout-text-tools
==================

A few scripts to ease the maintenance of Fallout's text files (1 and 2). Made for both practical and educational purposes (aka ugly code).

Made for Python 3.


====================
duplicate_checker.py
====================



====================
linebreak_remover.py
====================
    - Due to the layout of deadcomp.msg and fke_dude.msg, these files are skipped by default.



=================
syntax_checker.py
=================


=========
merger.py
=========
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


====================
General instructions
====================

To run this script you'll need to install version 3 of Python.
Download: http://www.python.org/download/

Then, associate the .py file with Python (python.exe, located wherever you installed it).
Then execute the .py file just by double clicking on it, and now a new window asking 
for input should appear.

Just put the script along with the .msg files (or folders conteining them) and run it. 