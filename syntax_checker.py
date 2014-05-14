import os, fnmatch


def pathfinder():
    filespaths = []
    for root, dirnames, filenames in os.walk('.'):
        for filename in fnmatch.filter(filenames, '*.msg'):
            filespaths.append(os.path.join(root, filename))
    return filespaths  

    
def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'): pass
    else: exit()


def syntax_checker(files):
    result = ''
    for file in files:
        
        occurrence = False
        
        with open(file, 'r') as rfile:
            lines = rfile.readlines()
        
        
        lines = [line for line in lines if line.startswith('#') is False]
        lines = [line for line in lines if line != '\n']
        lines = [line for line in lines if line]
        
        for line in lines:
            brackets = [character for character in line if character in ('{','}')]
            brackets = ''.join(brackets)
            npairs = brackets.count('{}')
            
            if npairs != 3 and not occurrence:
                occurrence = True
                result = result + file + "\n"
                
            if npairs < 3:
                result = result + "        Less tran three pairs -->   " + "'" + line.replace('\n','') + "'\n"
                
            elif npairs > 3:
                result = result + "        More than three pairs -->   " + "'" + line.replace('\n','') + "'\n"
        
        if occurrence:
            result = result + "\n\n"
        
        occurrence = False
    return result

    
    
if __name__ == "__main__":

    start_msg = "\n\
This script opens Fallout's .msg files, checks the syntax (open curly brackets)\n\
and saves a reference for any error found in a text file called 'sc-result'\n\
This version is much quicker and reliable but any line break inside brackets\n\
or dev comments that don't start with the usual number sign will raise\n\
a false positive. Use the line-break-remover to minimaze the false positives.\n\
You'll have to solve the problem manually, using the output text as reference.\n\
\n\
\n\
Type [y]es and hit enter to proceed or anything else to quit: "

    no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"

    help_msg = 175*"*" + "\n  Less tran three pairs of brackets: line break \
inside brackets (false positive), dev comment without number sign (ugly) or \
missing bracket/s (it would have cause a crash!)  \n More than three pairs of \
brackets: inline dev comment with brackets inside, two lines in one (not fatal \
but ugly) or a 'lost' set of brackets (it would have cause a crash!) \n" + 175*"*" + "\n\n\n"
    
    
    thefiles = pathfinder()
        
    if thefiles:  
        startcheck(start_msg)
    else: 
        print(no_files_msg)
        input()
        exit()

    print ("\n\nWORKING...\n\n")


    output = syntax_checker(thefiles)     
      
    if not output:
        output = "DONE! All files have correct syntax!"
        print (output)

    else:
        output = help_msg + output
        print ("DONE! There are syntax errors!")
        with open('sc-result.txt','w') as foutput:
            foutput.write(output)

                  
    input()
