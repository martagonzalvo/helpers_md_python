# This script will substitute given text in file, similar to vim function
# :%s/CD  ILE /CD1 ILE /gc
# For all files folder
# Usage:
#   python infilereplace.py folder (dict_keywords)
# Line 54 hardcoded for gpcr dictionary below, but could modify to read 
# from file or provide it elsewhere
# This is written for python 2.4 
# If using other python, need to fix strings and print statements.

import os, sys

def substitute_string(file_tomodify, path, dict_keywords=False):
    '''Changes lines of file IN PLACE. Could provide other dictionary
    than the one provided below.'''
    # dictionary of words to substitute
    # original : to_be_changed
    gpcrs = {
    'CD  ILE ' : 'CD1 ILE ',
    'HSE': 'HIE',
    'HSD': 'HID',
        }
    if dict_keywords==False:
        dict_keywords = gpcrs

    # Make new file with substituted lines
    linesfile = open(path+'/'+file_tomodify)
    newfile_name = 'subst_%s'%file_tomodify
    newfile = open(path+'/'+newfile_name, 'w')

    keys = dict_keywords.keys()
    for line in linesfile:
        line = line.split('\n')[0]

        for key in keys:
            if key in line:
                line = line.replace(key, dict_keywords[key])

        print >> newfile, line
    linesfile.close()
    newfile.close()

    return newfile_name


# so I can run substitute.py directly, but code below is not ran when imported
if (__name__ == '__main__'):
    #path = os.getcwd()
    folder = sys.argv[1]


    for filename in os.listdir(folder):
        # works with folder or path+'/'+folder
        substitute_string(filename, folder)


