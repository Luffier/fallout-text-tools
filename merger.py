import os, re, fnmatch

thefiles = []
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.msg'):
        thefiles.append(os.path.join(root, filename))

jump = '\n'
bar = '='
space = ' '

text = ''
result = ''
result_step = ''
dic_result = ''

left = len(thefiles)


description = "\n\
This script merges Fallout .msg files in one big file.\n\
This may come in handy for spotting isolated grammatical or spelling mistakes\n\
by using an aplication with this purpose (like MS Word).\n\
\n\
\n\
Type [y]es and hit enter to proceed or anything else to quit: "

des_comments = '\nDo you want to include developer comments (# lines)? '
des_indices = '\nDo you want to include the index number to each line (for reference; recommended)? '
des_names = '\nDo you want to include the name of the file to each line (for reference; recommended)? '
des_hf = '\nDo you want to include a header and footer to each block of text? '
des_dic = '\nDo you want to generate a dictionary for MS Word? '



def startcheck():
	inputcheck = input(description).lower()
	if inputcheck in ('yes','y'): pass
	else: exit()

def optionscheck():
    inputcheck_dev = input(des_comments).lower()
    if inputcheck_dev in ('yes','y'):
        option1 = True
    else: 
        option1 = False
        
    inputcheck_indices = input(des_indices).lower()
    if inputcheck_indices in ('yes','y'):
        option2 = True
    else: 
        option2 = False
        
    inputcheck_ref_name = input(des_names).lower()
    if inputcheck_ref_name in ('yes','y'):
        option3 = True
    else: 
        option3 = False
        
    inputcheck_hf = input(des_hf).lower()    
    if inputcheck_hf in ('yes','y'):
        option4 = True
    else: 
        option4 = False
        
    inputcheck_dic = input(des_dic).lower()    
    if inputcheck_dic in ('yes','y'):
        option5 = True
    else: 
        option5 = False
        
    return option1, option2, option3, option4, option5
    
   
startcheck()

comments, indices, names, header_footer, dic = optionscheck()

print ('\n\nWORKING...\n\n')

for file in thefiles:

    with open(file, 'r') as rfile:
        lines = rfile.readlines()
        
    filename = file[::-1]
    filename = filename[:filename.index('\\')]
    filename = filename[::-1]
    header = (len(filename)+32)*bar + jump + 12*bar + filename + '  BEGINS' + 12*bar + jump + (len(filename)+32)*bar + 4*jump
    footer = 4*jump +(len(filename)+32)*bar + jump + 12*bar + filename + '  ENDS' + 14*bar + jump + (len(filename)+32)*bar + 2*jump
    
    if dic:
        dic_result = dic_result + filename + jump + filename.replace('.MSG','') + jump
    
    if not header_footer:
        header = ''
        footer = ''
    
    for line in lines:
        if not comments:
            
            if re.findall(r'^\#', line) == ['#']:
                pass
            
            else:
                
                if re.findall(r'^\{', line) == ['{']:
                   
                    indexm = re.search(r'\{([0-9]*)\}', line)
                    index = line[indexm.start()+1:indexm.end()-1]
                    line = line[:indexm.start()+1] + line[indexm.end()-1:]
                    if re.search(r'\}$', line) == ['}']: 
                        line = line[:-1]  
                    contentm = re.search(r'\}\{(.*)\}\{', line)
                    line = line[contentm.end():-2] + jump
                    
                    if indices and names:
                        line = filename.replace('.MSG','') + space + index + space + line
                        
                    elif indices and not names:
                        line = index + space + line
                        
                    elif not indices and names:
                        line = filename.replace('.MSG','') + space + line
                        
                    elif not indices and not names: 
                        pass
                    
                    result_step = result_step + line
                    
        elif comments:
            
            if re.findall(r'^\{', line) == ['{']:
            
                indexm = re.search(r'\{([0-9]*)\}', line)
                index = line[indexm.start()+1:indexm.end()-1]
                line = line[:indexm.start()+1] + line[indexm.end()-1:]
                if re.search(r'\}$', line) == ['}']: 
                    line = line[:-1]
                contentm = re.search(r'\}\{(.*)\}\{', line)
                line = line[contentm.end():-2] + jump
                
                if indices and names:
                    line = filename.replace('.MSG','') + space + index + space + line
                
                elif indices and not names:
                    line = index + space + line
                
                elif not indices and names:
                    line = filename.replace('.MSG','') + space + line
                
                elif not indices and not names: 
                    pass
                
                result_step = result_step + line
            
            else: 
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