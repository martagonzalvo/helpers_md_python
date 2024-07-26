# File to convert trajectory to .pdb (only CA) using gromacs
# Usage:
#    python extractCAtrajectory.py foldersubfolders

import sys, os, time, subprocess

folder = sys.argv[1]

path = os.getcwd()
folderstorun = os.listdir(folder)
numfolders = len(folderstorun)

start_all = time.time()

for n, subfolder in enumerate(folderstorun):

    subpath = path+'/'+folder+'/'+subfolder
# make pdb of conly C-alphas
    subprocess.call('''gmx trjconv -f pbc_rotrans.xtc -s md_prod.gro -o ca_1.pdb << EOF
3
EOF''', cwd=subpath, shell=True)




