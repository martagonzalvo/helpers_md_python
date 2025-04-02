# Selects only last snapshot in pdb with several trajectory snapshots, and saves new file with only last as name_trunc.pdb in same folder


# python save_last_pdb_traj.py foldertodel

import os, sys

folder = sys.argv[1]
cwd = os.getcwd()

wordfind = 'step'

for file in os.listdir(cwd+'/'+folder):

    if 'pdb' not in file:
        continue

    with open(cwd+'/'+folder+'/'+file, 'r') as f:
        lines = f.read()

        # find last occurrence of 'step' in the PDB, which is in the header of the structure
        stepind = lines.rfind('step')

        truncated=lines[stepind+15:]
    
    filename = file.split('.')[0]

    with open(cwd+'/'+folder+'/'+filename+'_trunc.pdb', 'w') as nf:
        nf.writelines(truncated)    

    print(file)



