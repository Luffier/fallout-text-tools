import os, re, fnmatch


def pathfinder():
    filespaths = []
    for root, dirnames, filenames in os.walk('.'):
        for filename in fnmatch.filter(filenames, '*.msg'):
            filespaths.append(os.path.join(root, filename))
    return filespaths  

thefiles = pathfinder()

jump = '\n'
bar = '='
space = ' '

text = ''
result = ''
result_step = ''
dic_result = ''

left = len(thefiles)


start_msg = "\n\
This script merges Fallout .msg files in one big file.\n\
This may come in handy for spotting isolated grammatical or spelling mistakes\n\
by using an aplication with this purpose (like MS Word).\n\
\n\
\n\
Type [y]es and hit enter to proceed or anything else to quit: "


no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"


comments_msg = '\nDo you want to include developer comments (# lines)? '
indices_msg = '\nDo you want to include the index number to each line (recommended)? '
names_msg = '\nDo you want to include the name of the file to each line (recommended)? '
hf_msg = '\nDo you want to include a header and footer to each block of text? '
dic_msg = '\nDo you want to generate a dictionary for MS Word (little use)? '



def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes','y'): pass
    else: exit()

def optionscheck():
    inputcheck_dev = input(comments_msg).lower()
    if inputcheck_dev in ('yes','y'):
        option1 = True
    else: 
        option1 = False
        
    inputcheck_indices = input(indices_msg).lower()
    if inputcheck_indices in ('yes','y'):
        option2 = True
    else: 
        option2 = False
        
    inputcheck_ref_name = input(names_msg).lower()
    if inputcheck_ref_name in ('yes','y'):
        option3 = True
    else: 
        option3 = False
        
    inputcheck_hf = input(hf_msg).lower()    
    if inputcheck_hf in ('yes','y'):
        option4 = True
    else: 
        option4 = False
        
    inputcheck_dic = input(dic_msg).lower()    
    if inputcheck_dic in ('yes','y'):
        option5 = True
    else: 
        option5 = False
        
    return option1, option2, option3, option4, option5
    
    
    
   
if thefiles:  
    startcheck(start_msg)
else: 
    print(no_files_msg)
    input()
    exit()
  
comments, indices, names, header_footer, dic = optionscheck()



print ('\n\nWORKING...\n\n')



for file in thefiles:

    with open(file, 'r') as rfile:
        lines = rfile.readlines()
        
    filename = file[::-1]
    filename = filename[:filename.index('\\')]
    filename = filename[::-1]
    header = (len(filename)+32)*bar + jump + 12*bar + filename + '  BEGINS' + 12*bar + jump + (len(filename)+32)*bar + 4*jump
    footer = 3*jump +(len(filename)+32)*bar + jump + 12*bar + filename + '  ENDS' + 14*bar + jump + (len(filename)+32)*bar + 2*jump
    
    if dic:
        dic_result = dic_result + filename + jump + filename.replace('.MSG','') + jump
    
    if not header_footer:
        header = ''
        footer = ''
    
    for line in lines:
    
        if line.startswith('{'):
            indexm = re.search(r'^\{[0-9]+\}', line)
            index = line[indexm.start()+1:indexm.end()-1]
            line = line[indexm.end()+2:]
            
            contentm = re.findall(r'\{(.+)\}', line)
            
            if contentm:
                content = contentm[0]
            else:
                content = ''
            
            line = content + jump
            
            if indices and names:
                line = filename[:-4] + space + index + space + line
            
            elif indices and not names:
                line = index + space + line
            
            elif not indices and names:
                line = filename[:-4] + space + line


            result_step = result_step + line
        
        elif line == '\n':
            break
        
        elif comments:
            line = filename[:-4] + space + line
            result_step = result_step + line

                    
    result = result + header + result_step + footer
    result_step = ''
    left = left - 1
    fbars = 43-len(filename) 
    print (filename + ' DONE ' + '-'*fbars + '>  ' + str(left) + ' files left.')


try: 
    with open('merged_text.txt', 'w') as output:
        output.write(result)

except PermissionError: 
    print ('\n\nERROR. merged_text.txt is open in another program. Close it and try again.\n\n')
    input()
    exit()

if dic:
    try: 
        with open('merged_text.dic', 'w', encoding='utf16') as dic_file:
            dic_file.write(dic_result)

    except PermissionError: 
        print ('\n\nERROR. merged_text.dic is open in another program. Close it and try again.\n\n')
        input()
        exit()

        
print ('\n\nDONE!')
input()