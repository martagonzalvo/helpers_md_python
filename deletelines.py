# Script to delete lines in file. Two modalities:
# - lines with strings found in other text file. 
# - first n lines of the file
# - after line n of file
# It does so for for every file in filestomodify and will write new files
#  with the same name in folder deletedkw (intermediates in folder deletedlines)
# RIGHT NOW NEED TO CHANGE OUTPUT FUNCTION IN LINE 65 TO RUN THIS .PY FILE 
# IF WANT one modality only  INSTEAD OF both
#
# Usage:
#       python deletelines.py filestomodify filewithlines nbegin nend

#       - "filestomodify" is a folder with all pdbs needed to be cleaned
#       - "filewithlines" is a text file with each line is a different keyword
#       to be found in files in the folder filetomodify. Each line in a 
#       filetomodofy that has a keyword from filewithlines will be deleted. If 
#       empty file, does nothing.
#       - "nbegin" is the number of lines to be deleted at the beginning of the file
#       - "nend" is number of the last line to keep of the file. after this line number, all lines are deleted
#               - if nend == 0, then doesn't delete any lines at the end
# This is written for python 3
# took 170 s for 118 files of about 400,000 lines = 1.4s/file


import os, sys, time, subprocess

def delete_lines_kw(file_tomodify, file_withkeywords, path):
        if not os.path.exists(path+'/deletedkw/'):
                os.mkdir(path+'/deletedkw/')
        # Make list from file with 1 keyword per line
        keywords_file = open(file_withkeywords)
        keywords = keywords_file.readlines()
        keywords_file.close()

        # Make new file with only lines without keywords
        linesfile = open(path+'/deletedlines/'+file_tomodify)
        #newfile_name = 'delkw_%s'%file_tomodify
        newfile = open(path+'/deletedkw/'+file_tomodify, 'w')
        for line in linesfile:
                printing=True
                for keyword in keywords:
                        key = keyword.split('\n')[0]
                        if key=='':
                                continue
                        if key=='\n':
                                continue
                        if key in line:
                                printing=False
                                break
                if printing==True:   
                        newfile.writelines(line) 
        linesfile.close()
        newfile.close()

        return 

def delete_lines_n(file_tomodify, nbegin, nend, path):
        if not os.path.exists(path+'/deletedlines/'):
                os.mkdir(path+'/deletedlines/')

        # Make new file with only lines without keywords
        linesfile = open(path+'/'+file_tomodify)
        #newfile_name = 'deln_%s'%file_tomodify
        newfile = open(path+'/deletedlines/'+file_tomodify, 'w')

        nbegin = int(nbegin)
        nend = int(nend)
        for i, line in enumerate(linesfile):
                line = line.split('\n')[0]
                if i < nbegin:
                        continue               
                else:
                        newfile.writelines(line+'\n') 
                if nend==0:
                        continue
                if i > nend:
                        break  
        linesfile.close()
        newfile.close()

        return 


# so I can run deletelines.py directly, but code below is not ran when imported
if (__name__ == '__main__'):
        folder = sys.argv[1]
        file_kw = sys.argv[2]
        file_todel_nbegin = sys.argv[3]
        file_todel_nend = sys.argv[4]
        start = time.time()
        

        for filename in os.listdir(folder):
                if '.pdb' not in filename:
                        continue
                # works with folder or path+'/'+folder
                
                newfile = delete_lines_n(filename, file_todel_nbegin, file_todel_nend, folder)

                delete_lines_kw(filename, file_kw, folder)

        # deleting unused files and moving files to truncated files folder
        subprocess.call('rm -r deletedlines', cwd=folder, shell=True)
        subprocess.call('mv deletedkw trunc_files', cwd=folder, shell=True)

        print('Finished processing files in this many seconds', time.time()-start)
        print('Final files are in {}/trunc_files/'.format(folder))