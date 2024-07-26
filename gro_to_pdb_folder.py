# changes all .gro files in folder to .pdb with same name
# usage:
#   python gro_to_pdb_folder.py foldergrofiles


import sys, os, time, subprocess

folder = sys.argv[1]

path = os.getcwd()
filestorun = os.listdir(folder)
numfiles = len(filestorun)

start_all = time.time()

for n, file in enumerate(filestorun):

    if '.gro' not in file:
        continue
    folderpath = path+'/'+str(folder)

    filename = file.split('.')[0]
    print('Changing file {} to {}.pdb'.format(file, filename))
    subprocess.call('''gmx editconf -f {} -o {}.pdb'''.format(file, filename), cwd=folderpath, shell=True)
    

time_all = time.time() - start_all
print('It took {} seconds to fully change all {} files in parent folder {}'.format(time_all, numfiles, folder))
print('Files changed from .gro to .pdb')
print('Will rewrite everything if script run again')
