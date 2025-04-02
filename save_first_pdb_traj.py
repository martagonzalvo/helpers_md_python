# Selects only first snapshot in pdb with several trajectory snapshots, and saves new file with only first as name_trunc.pdb in same folder

# python save_first_pdb_traj.py foldertodel



import os, sys

folder = sys.argv[1]
cwd = os.getcwd()

wordfind = 'REMARK'

for file in os.listdir(cwd+'/'+folder):

    if 'pdb' not in file:
        continue

    with open(cwd+'/'+folder+'/'+file, 'r') as f:
        lines = f.read()

        # find third occurrence of 'REMARK' in the PDB, which is the first line of the 2nd structure
        first = lines.find(wordfind)
        second = lines.find(wordfind,first+len(wordfind))
        third = lines.find(wordfind,first+second+len(wordfind))

        truncated=lines[:third]
    
    filename = file.split('.')[0]

    with open(cwd+'/'+folder+'/'+filename+'_trunc.pdb', 'w') as nf:
        nf.writelines(truncated)    

    print(file)



