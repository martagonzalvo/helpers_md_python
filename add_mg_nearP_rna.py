# puts 1 MG/CA every 2 phosphates, using closest neighbor
# use on solvated pdb without ions, with water

# usage:
#   python add_mg_nearP_rna.py dup_solvmer.gro CA/MG

# outputs 
# - new dup_solvmermod.gro
# - new modified topol.top

# need to run from pdb2gmx command, from scratch! otherwise topol not work well

# gmx pdb2gmx -f substituted.pdb -o duplexgmxmer.pdb -water tip3p -ignh -ff amber14sblnaintorna -missing
# gmx editconf -f duplexgmxmer.pdb -o dup_boxmer.pdb -c -d 1 -bt cubic 
# gmx solvate -cp dup_boxmer.pdb -o dup_solvmer.gro -p topol.top
# python ~/scripts/md_gmx/addmgph.py dup_solvmer.gro CA

# gmx grompp -f ions.mdp -c dup_solvmermod.gro -p topol.top -o ions.tpr -maxwarn 2
# gmx genion -s ions.tpr -o dup_na.gro -p topol.top -pname NA -np {}
# gmx grompp -f ions.mdp -c dup_na.gro -p topol.top -o ions.tpr -maxwarn 2
# gmx genion -s ions.tpr -o dup_ions.gro -p topol.top -pname NA -nname CL -conc 0.154 
# gmx make_ndx -o index.ndx -f dup_ions.gro

import sys, os 
import mdtraj as md
import numpy as np, pandas as pd

def add_resnum_topo(traj,topo):
    # adds residue names and numbers to topo df as mdtraj reads it 
    resiter = []
    for _, name in enumerate(traj.topology.atoms):
        removename = str(name).split('-')[-1] # remove atom name and only resname remaining (otherwise not work bc some res have - index numbers)
        res = str(name).replace('-'+removename, '')
        #res = str(name).split('-')[0]
        resiter.append(res)  
    topo['residue'] = resiter
    
    uniqueres = topo['residue'].unique()
    indres = np.linspace(0,len(uniqueres),len(uniqueres)+1, dtype=int)
    dictres = dict(zip(uniqueres, indres))
    topo['resnum'] = topo['residue'].apply(lambda x: dictres[x])
    return topo

# loading all files
cwd = os.getcwd()

file = sys.argv[1]
ion = sys.argv[2]

possibleions = ['CA', 'MG']

if ion not in possibleions:
    print('Ion not from list of possible ions. Please supply ion from the following options: ', possibleions)

print('Loading files')
traj = md.load(cwd+'/'+file)
topo, _ = traj.topology.to_dataframe()


with open(cwd+'/'+file) as f:
    grofile =  f.readlines()

# cleaning up files and getting indeces P, waters
topores = add_resnum_topo(traj,topo)

index_phosphates = topo[topo['name']=='P'].index
index_wat = topo[topo['resName'].str.contains('HOH')].index

# do 1st neighbors to find waters near P, create traj object with only P and close waters, then compute contacts within that new subtraj object
watneighborph = md.compute_neighbors(traj, 0.5,index_phosphates,index_wat)
index_watcloseph = np.concatenate((index_phosphates,watneighborph[0]))

watphostraj = md.Trajectory.atom_slice(traj, index_watcloseph)

watphoscont= md.compute_contacts(watphostraj, contacts='all', scheme='closest', ignore_nonprotein=False)


# getting new residue numbers in created traj/topo for each atom
topowatphos, _ = watphostraj.topology.to_dataframe()
topowatphos = add_resnum_topo(watphostraj,topowatphos) 


# analyzing contacts and cleaning up
contacts = pd.DataFrame(watphoscont[0].T, columns=['distance'])
contacts['first'] = watphoscont[1].T[0]
contacts['second'] = watphoscont[1].T[1]

phosphateresnew = topowatphos[topowatphos['element'] =='P']['resnum']

                           
contacts['firstp'] = contacts['first'].apply(lambda x: x in phosphateresnew)
contacts['secondp'] = contacts['second'].apply(lambda x: x in phosphateresnew)

contacts['samegroup'] = contacts['firstp'] == contacts['secondp']

difgroups = contacts[contacts['samegroup']==False]

mincontacts = pd.DataFrame(columns=difgroups.columns)
waters = []
for nameg, group in difgroups.groupby(['first']):
    mincontact = group[group['distance'] ==group['distance'].min()]

    while mincontact['second'].values in waters:
        #print(mincontact['second'], waters)
        newgroup = group.drop(index=mincontact.index)
        mincontact = newgroup[newgroup['distance'] ==newgroup['distance'].min()]

    waters.append(mincontact['second'].values.item())

    mincontacts = pd.concat([mincontacts,mincontact])

# find waters to substitute, put CA with same coord as O at end of file
print('Placing CA or MG nearest to every other P')

linestodel = []
canum = 1


lastatom = int(grofile[-2].split('HW2')[1].split(' ')[0])
lastres = int(grofile[-2].split('SOL')[0])
for index, row in mincontacts.iterrows():


    if int(row['first']) %2 != 0:
        continue
    else:
        indexwat = row['second']
        # print(indexwat)
        # print(topowatphos[topowatphos['resnum']==indexwat])
        restopowatphos = topowatphos[topowatphos['resnum']==indexwat]
        # print(restopowatphos)
        # print(restopowatphos['residue'])
        residue = restopowatphos['residue'].unique()[0]

        watrows= topores[topores['residue'] == residue] 
        indexo = watrows.index[0]

        rowsubst = grofile[indexo+2]

        if len(str(canum)) == 1:
            addcanum=' '+str(canum)
        else:
            addcanum=str(canum)

        newrow = str(lastres+int(addcanum))+'{} '.format(ion)+'     '+'{}'.format(ion)+str(lastatom+int(addcanum))+'  '+rowsubst[22:]
        grofile = grofile[:-1]+[newrow]+[grofile[-1]]

        linestodel.append(residue[3:])
        canum +=1


# delete waters substituted
for res in linestodel: 


        if len(res) < 5:
            res =  ' '+res
        todel = res+'SOL'

        grofile = [el for el in grofile if todel not in el]


# adjusting new number of molecules
grofile[1] = str(int(grofile[1]) - len(linestodel*2)) + '\n'

# saving new gro file
with open(cwd+'/'+file.split('.')[0]+'mod.'+file.split('.')[1], "w") as f:
    f.writelines(grofile)


# need fix number of atoms in top file too
with open(cwd+'/topol.top') as f:
    topofile =  f.readlines()

for i,line in enumerate(topofile):
    if 'SOL' in line:
        molwats = line.split(' ')[-1]
        print(molwats)
        molwats = int(molwats) - len(linestodel)
        print(molwats)
        newsol = 'SOL            '+str(molwats)+'\n'
        numcas = '{}               '.format(ion)+str(len(linestodel))+'\n'
        topofile=topofile[:i]+[newsol]+topofile[i+1:]+[numcas]

with open(cwd+'/topol.top', "w") as f:
    f.writelines(topofile)