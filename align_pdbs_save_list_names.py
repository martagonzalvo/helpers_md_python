# from a directory with pdbs, 
#   aligns all pdbs to given reference and saves all pdbs into single (very large file).
#   also saves aligned pdbs into separate files
#   saves a summary csv file with namefile
#   also saves errorfile with files not aligned+saved


# It will align even if not same topology (saving pdbnameal.pdb), but won't add to single large pdb file with all aligned if not exact topology (num chains, name atoms)

## HARDCODED INDICES ALIGN BY GALPHA RAS DOMAIN! from pdbs with deleted GPCRs, sweetener ligands (RES, RebM,...) -- lines 49 and 50

# usage:
#   python align_pdbs_save_list_names.py folder reference.pdb

#   python align_pdbs_save_list_names.py gdpclustering gdpclustering/isorebmPam_dM1open_465588.pdb  

#   - folder is folder of pdbs to align
#       - pdbs need to have chain ID = to ref (= mdtraj topology: # chains, atoms)
#           - if not present, can add from reference (if # atoms is the same) with add_chainid_pdb.py
#   - referencepdb is single pdb structure to serve as reference

# Returns /aligned/ folder with 
#   - aligned individual pdbs
#   - allnames... .txt with names of aligned pdbs
#   - erred... .txt with names of files not aligned bc error
#   - allaligned_... .pdb single file with all pdbs aligned

# Aligned 120 files in 97.98660111427307 seconds, 1 weren't pdbs, 33 erred



import mdtraj as md
import numpy as np
import os, sys, time, shutil

folder = sys.argv[1]
referencepdb = sys.argv[2]

start = time.time()

referencestruct = md.load(referencepdb)

# Getting index numbers to align by Galpha, RAS domain
# will also do betagamma
# HARDCODED!!

topo, _ = referencestruct.topology.to_dataframe()

RAS = np.concatenate((np.linspace(57,1, 57-1+1, dtype=int),np.linspace(180,353, 353-180+1, dtype=int)))
RAS_CAs = topo[[res in RAS for res in topo['resSeq']] & (topo['chainID']==2) & (topo['name']=='CA')].index

# apparently can also do: selection = topology.select_expression('name CA and resid 1 to 2')

merged = referencestruct

numfiles = len(os.listdir(folder)) 
notpdb = 0
erred = 0
aligned = 0

if os.path.exists(folder+'/aligned'):
    shutil.rmtree(folder+'/aligned')

os.mkdir(folder+'/aligned')

for fnum, filestruct in enumerate(os.listdir(folder)):
    filename = filestruct.split('.')[0]

    if '.pdb' not in filestruct:
        notpdb +=1
        continue
    try: 
        toalign = md.load(folder+'/'+filestruct)
        
        alignedstruct = md.Trajectory.superpose(toalign, referencestruct, atom_indices=RAS_CAs)

        # this changes toalign, toalign == alignedstruct
        # save xyz coordinates, also aligned pdb on its own - only saving pdb for now

        md.Trajectory.save_pdb(alignedstruct, folder+'/aligned/'+str(filename)+'al.pdb')

        # merged all struct together to save later
        merged = md.Trajectory.join(merged, alignedstruct)

        # save names only list
        with open(folder+'/aligned/allnames{}.txt'.format(folder), 'a') as f:
            f.writelines(filename+'\n')
        
        print('{}/{}, {}'.format(fnum, numfiles, filename))
        aligned +=1
    
    except Exception as e:
        print("Couldn't do structure {}".format(filename))
        print(e)
        erred +=1
        with open(folder+'/aligned/erred{}.txt'.format(folder), 'a') as f:
            f.writelines(filename+'\n')
        continue

print('\n \n Saving single pdb all structures \n \n')

# saves 1st reference, then other models
md.Trajectory.save_pdb(merged, folder+'/aligned/allaligned_{}.pdb'.format(folder)) 


print("Aligned {} files in {} seconds, {} weren't pdbs, {} erred, total files {}".format(aligned, time.time()-start, notpdb, erred, numfiles))
print('Final files are in {}/aligned'.format(folder))