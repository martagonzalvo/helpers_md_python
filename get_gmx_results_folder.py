# Copies xtc and gro files from simulation folders to results folder where they are renamed based on origin folder
# makes .pdb files from gro and xtc files
# Will look for files of desired run that contain "namerun", e.g. "md10ns" or "protequil", and if doesn't find it will use nvt as structure file

# Run inside of folder where all subset of simulation folders run:

# Usage:
#   python get_gmx_results_folder.py namerun


import os, shutil, subprocess, sys

namerun = sys.argv[1]

cwd = os.getcwd()

# make results folder if doesn't exist
if not os.path.exists(cwd+'/results'):
    os.mkdir(cwd+'/results')


# copy only not existing .gro and .xtc files in results, print missing ones (still running or error)
notfinished = []

for folder in os.listdir():
    if 'results' in folder:
        continue
    if '.' in folder:
        continue
    name1 = folder.replace('evoths','')
    name = name1.replace('dup','')

    grores = cwd+'/results/'+name+'{}.gro'.format(namerun)
    xtcres = cwd+'/results/'+name+'{}.xtc'.format(namerun)
    nvtres = cwd+'/results/'+name+'nvt.gro'

    if not os.path.exists(xtcres):
        print('here')
        if os.path.exists(folder+'/{}.xtc'.format(namerun)):
            print('copying ',xtcres)
            shutil.copy(folder+'/{}.xtc'.format(namerun), xtcres)

    if not os.path.exists(grores):
        print('gros')
        if os.path.exists(folder+'/{}.gro'.format(namerun)):
            print('copying',grores)
            print(folder+'/{}.gro'.format(namerun), grores)
            shutil.copy(folder+'/{}.gro'.format(namerun), grores)
        elif os.path.exists(folder+'/nvt.gro'):
            print('copying',nvtres)
            shutil.copy(folder+'/nvt.gro', nvtres)
            notfinished.append(folder)
        else:
            print("This folder hasn't run",folder)


# printing missing files     
print('ALL DONE! FILES ARE IN ',cwd+'/results')
if notfinished != []:
    print('Some files are still running, erred, or are not simulations:')
    print("Wasn't able to do the following, need to do manually:")
    for file in sorted(notfinished):
        print(file)




# making pdb files from files with gro

for xtcfile in os.listdir(cwd+'/results'):
    name = xtcfile.split('md')[0]

    section = xtcfile.split('.')[0]

    if 'xtc' not in xtcfile:
        continue
    if os.path.exists(cwd+'/results/'+name+'.pdb'):
        continue

    number =  1


    file = name+'md10ns.gro'
    print(file)
    if not os.path.exists(cwd+'/results/'+file):
        file = name+'nvt.gro'
        subprocess.call("""gmx_mpi trjconv -f {} -s {} -dt 500 -o {}.pdb -pbc nojump <<EOF
        {} 
        EOF""".format(xtcfile, file, section, number), cwd=cwd+'/results', shell=True) 
        continue 

    subprocess.call("""gmx_mpi trjconv -f {} -s {} -dt 500 -o {}.pdb -pbc nojump <<EOF
    {}
    EOF""".format(xtcfile, file, section, number), cwd=cwd+'/results', shell=True)


        
    
