
# Copies script with field "REPLACE" to be changed for each folder it is copied into 

# Need original script in same fodler as simulation folders
# Usage:
#   python copy_file_folder_replace_name.py namescript


import sys,  os


script = sys.argv[1]

path = os.getcwd()

with open("{}/{}".format(path, script), 'r') as f:
        file = f.read()

for folder in os.listdir():


    cwd = path+'/'+folder
 
    with open("{}/{}/{}".format(path, folder, script), 'r') as f:
        ogfile = f.readlines()

    newfile = file.replace("REPLACE", "{}".format(folder))

    with open("{}/{}".format(cwd, script), 'w') as f:
        f.write(newfile)
