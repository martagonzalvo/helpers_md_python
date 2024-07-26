# script to calculate rmsd of structures in folders 
# Usage: 
#   python rmsd.py folder_compare folder_references
# Where the rmsd of all structures in foldertocomparermsd will be 
# compared to the reference structure of the same name in folder_references.
# Every file in folder_compare must have an equivalent file in folder_references.
# Outputs: 
#   folder_rmsds.txt 
# File with list of rmsds 

#previously: for triad mutations folders and original files hardcoded! 


import mdtraj, sys, time, os
from Bio.SVDSuperimposer import SVDSuperimposer
sup = SVDSuperimposer()

start = time.time()
tocompare = sys.argv[1]
references = sys.argv[2]

path = os.getcwd()

outputfile = tocompare+'_rmsds.txt'

def rmsd(compared, reference, sup):
    ''' Takes path to reference and compared structures in pdb format.
    Returns SVDSuperimposer rms'''
    
    str_ref = mdtraj.load(str(reference))
    str_compare = mdtraj.load((str(compared)))
    print(compared, reference)
    print(str_ref)
    print(str_compare)
    sup.set(str_compare.xyz, str_ref.xyz)
    sup.run()
    rms = sup.get_rms()
    return rms

n=0
for filename in os.listdir(tocompare):
    if '.pdb' not in filename:
        continue
    rms = rmsd(path+'/'+tocompare+'/'+filename, path+'/'+references+'/'+filename, sup)
    allrmsds = open(outputfile, "a")
    print(filename+ '    '+rms, file=allrmsds)
    rms = 0
    allrmsds.close()
    n=1
totaltime = time.time()-start    

print('Finished calculating rmsd of {} files, took {} seconds. Results are in file {}'.format(n, totaltime, outputfile))