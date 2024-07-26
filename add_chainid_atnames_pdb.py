# adds chain ID so structure can be used in CHARMM-GUI 
# (structure from .gro to .pdb doesn't save chain ID info)
# Added functionality so also substitutes atom names
# CAREFUL! NEED TO CHECK MANUALLY THAT WON'T BE MESSING UP STRUCTURE, AND THAT ATOM DIFFERENCES ARE ONLY BC NOTATION AND NOT DIFFERENT IDENTITY

# IF USING STRUCTURE POST SIMULATION, NEED TEMPLATE WITH HYDROGENS!!

# usage: 
#   python add_chainid_atnames_pdb.py template.pdb tomodify.pdb newfile.pdb (yesatoms)

#   python add_chainid_atnames_pdb.py template.pdb tomodify.pdb newfile.pdb yes

            # template.pdb is pdb of the same structure and number of atoms and
            #       ordering that has the correct chain ID info, but different 
            #       coordinates. First line is "CRYST1 ...", has to have "MODEL"
            #       in 2nd line
            # tomodify.pdb is pdb of structure that needs chainID added to. Has 
            #       same number of atoms and order (only protein) as template, 
            #       different coordinates. First line is "CRYST1 ...", has to 
            #       have "MODEL" in 2nd line
            # newfile.pdb is name of what tomodify data will be with added chains
            # yesatoms is an optional parameter: if present, script will also 
            #       substitute atom names. Any character/string/number will do:
            #       only matters whether present or not

#### RIGHT NOW MODIFIED! WON'T DO MODEL BC WORKING WITH TRUNCATED FILES- IF WANT, SET BEGINTEMP=FALSE AT BEGINNING OF EACH WITH...OPEN()



import sys


def addchainid_names(template, tomod, newfile, substituteatoms):
    lookfor = 'MODEL'

    # Reading and making list of ChainIDs
    with open(str(template)) as f:
        chainids = []
        atomnames = []
        ntemp = 0
        begintemp = True # this needs to be false for pdbs not truncated, where lines above model and coordinates
        for i, line in enumerate(f.readlines()):
            chainid = None
            nameat=None

            # only do up to GDP, NO RES or MG
            if "END" in line or "RES" in line:
                break
            if begintemp:
                if len(line) < 21:
                    print('skipping this line \n',line)
                    continue
                origline = line
                chainid = origline[21]
                chainids.append(chainid)

                if substituteatoms:
                    nameat = origline[12:17]
                    atomnames.append(nameat)

                ntemp += 1
                continue
            if lookfor in line: 
                begintemp = True # CHECK THIS 

    print(len(chainids))
    # Reading and copying contents tomodify file
    with open(str(tomod)) as f:
        newlines = []
        nmod = 0
        begintomod = True # this needs to be false for pdbs not truncated, where lines above model and coordinates
        for i, line in enumerate(f.readlines()):
            # only do up to GDP, NO RES or MG
            if "END" in line or "RES" in line or "TER" in line: ### THIS MODIFIED FOR SIRNA! MIGTH FAIL FOR GPCRS!
                break
            if line == "TER":
                continue
            if begintomod:

                # if already has chain ids - DON'T PRINT
                if len(line) < 21:
                    print('skipping this line \n',line)
                    continue
                if line[21] != " " and line[21] != "":
                    print("Already has chainIDs, won't print")
                    break
                origline = line
                if substituteatoms:
                    newline = origline[:12]+str(atomnames[nmod])+origline[17:21]+str(chainids[nmod])+origline[22:]
                else:
                    print(origline)
                    print(nmod)

                    newline = origline[:21]+str(chainids[nmod])+origline[22:]
                newlines.append(newline)
                nmod += 1
                continue
            if lookfor in line: 
                begintomod = True
            newlines.append(line)

    print(ntemp, nmod)
    if ntemp != nmod:
        print("""DIDN'T HAVE SAME NUMBER OF LINES!
        CANCELING PRINTING NEW FILE""")

    # Saving into new file
    if ntemp == nmod:
        with open(str(newfile), "w") as f:
            f.writelines(newlines)
        return


# so I can run script directly, but code below is not ran when imported
if (__name__ == '__main__'):
    template = sys.argv[1]
    tomod = sys.argv[2]
    newfile = sys.argv[3]

    substituteatoms = False
    if len(sys.argv) >4:
        substituteatoms=True
        print('WILL ALSO SUBSTITUE ATOMS OF {} for atoms of {}'.format(tomod, template))
    
    addchainid_names(template, tomod, newfile, substituteatoms)
    
