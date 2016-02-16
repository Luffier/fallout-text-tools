import os, re, sys

from common import *


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
\n\n\
[y]es and hit enter to proceed or anything else to quit: "


no_files_msg = "\n\
There are no .msg files in this directory (the script makes a recursive search).\n\
Hit enter to quit and try again.\n"


comments_msg = '\nDo you want to include developer comments (# lines)? '
indices_msg = '\nDo you want to include the index number to each line (recommended)? '
names_msg = '\nDo you want to include the name of the file to each line (recommended)? '
hf_msg = '\nDo you want to include a header and footer to each block of text? '
dic_msg = '\nDo you want to generate a dictionary for MS Word (little use for now)? '



def startcheck(message):
    inputcheck = input(message).lower()
    if inputcheck in ('yes', 'y'):
        pass
    else:
        sys.exit(1)


def optionscheck(questions):
    answers = []
    for question in questions:
        inputcheck = input(question).lower()
        if inputcheck in ('yes', 'y'):
            answers.append(True)
        else:
            answers.append(False)

    return answers


if thefiles:
    startcheck(start_msg)
else:
    sys.exit(no_files_msg)

comments, indices, names, header_footer, dic = optionscheck( [comments_msg, indices_msg, names_msg, hf_msg, dic_msg] )


print('\n\nWORKING...\n\n')


dirnames = listdirs()
for dirname in dirnames:


    other_dirs = [d for d in dirnames if d is not dirname]
    thefiles = pathfinder(excluded=other_dirs)
    enc = encfinder(dirname)

    for afile in thefiles:

        par = [enc, None] #parameters = [enconding, errors]
        lines = alt_read(afile, par)

        filename = os.path.split(afile)[-1]

        header = (len(filename)+32)*bar + jump + 12*bar + filename + '  BEGINS' + 12*bar + jump + (len(filename)+32)*bar + 4*jump
        footer = 3*jump +(len(filename)+32)*bar + jump + 12*bar + filename + '  ENDS' + 14*bar + jump + (len(filename)+32)*bar + 2*jump

        if dic:
            dic_result = dic_result + filename + jump + filename[:-4] + jump

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
        #print(filename + ' DONE ' + '-'*fbars + '>  ' + str(left) + ' files left.')


    try:
        with open('merged_text-%s.txt' % dirname, 'w', encoding=par[0]) as output:
            output.write(result)

    except PermissionError:
        sys.exit('\n\nERROR. merged_text.txt is open in another program. Close it and try again.\n\n')

    if dic:
        try:
            with open('merged_text.dic', 'w', encoding='utf_16') as dic_file:
                dic_file.write(dic_result)

        except PermissionError:
            sys.exit('\n\nERROR. merged_text.dic is open in another program. Close it and try again.\n\n')


    print('\n\n%s done!' % dirname)

print('ALL DONE!')
input()
