import os

from linebreak_remover import linebreak_remover, pathfinder, dircreator
from syntax_checker import syntax_checker
from duplicate_checker import duplicate_checker


outputdir = 'output'

help_msg = 175*"*" + "\n  Less tran three pairs of brackets: line break \
inside brackets (false positive), dev comment without number sign (ugly) or \
missing bracket/s (it would have cause a crash!)  \n More than three pairs of \
brackets: inline dev comment with brackets inside, two lines in one (not fatal \
but ugly) or a 'lost' set of brackets (it would have cause a crash!) \n" + 175*"*" + "\n\n\n"

no_files_msg = "\n\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"


thefiles = pathfinder(excludedirs = [outputdir])

if not thefiles:
    print(no_files_msg)
    input()
    exit()

dircreator(thefiles, outputdir)

def startcheck():
    answer = input("Do you want to exclude the [d]efault files (fke_dude.msg and deadcomp.msg), \n\
[n]one or [o]ther?: ")
    if answer in ('default','d'):
        excluded = ['fke_dude.msg','deadcomp.msg']
    elif answer in ('none','n'):
        excluded = []
    elif answer in ('others','other','o'):
        excluded = input("\nWhich ones?\n\
(Type the filename -with extension- and if more than one separate with spaces,\n\
just like this: 'file1.msg file2.msg')\n\n")
        excluded.lower()
        excluded.split()
    else: exit()
    return excluded

excluded_files = startcheck()






print("\nSTEP 1/3: Running line break remover...\n")

result1 = linebreak_remover(thefiles, outputdir, excluded = excluded_files, allmode = True)

if not result1:
    input("\n\nThere weren't any lines breaks or unnecessary spaces.\n\
Hit enter to continue.\n\n\n\n")
else:
    print( '========================================' )
    print( 'Number of files: %i (%i excluded)' % (result1[0], result1[1]) )
    print( 'Number of files changed: %i' % result1[2] )
    print( 'Line breaks toll: %i' % result1[3] )
    print( 'Unnecessary spaces toll: %i' % result1[4] )
    print( '========================================' )
    
    input("\nAll lines breaks and unnecessary spaces have been removed.\n\
Hit enter to continue.\n\n\n\n")






print("\nSTEP 2/3: Running syntax checker...\n")

targetdir = os.path.join('.', outputdir)

thefiles = pathfinder(target = targetdir)

result2 = syntax_checker(thefiles)

if not result2:
    input("There weren't any syntax errors.\n\
Hit enter to continue.\n\n\n\n")
else:
    result2 = help_msg + result2
    with open('sc-result.txt','w') as fresult2:
        fresult2.write(result2)
    input("All syntax errors have been recorded in 'sc-result.txt'.\n\
Now, using it as reference, fix all the files manually (those inside 'output').\n\
Done? Hit enter to continue.\n\n\n\n")





print("\nSTEP 3/3: Running duplicate checker...\n")

thefiles = pathfinder(target = targetdir)

result3 = duplicate_checker(thefiles)

if not result3:
    input("There weren't any duplicate lines. \n\
Hit enter to quit.")
else:
    result3 = result3
    with open('dc-result.txt','w') as fresult3:
        fresult3.write(result3)
    input("All duplicate lines have been recorded in 'dc-result.txt'. \n\
Now, using it as reference, fix all the files manually (those inside 'output').\n\
Done? Congratulations, you have finished.")
