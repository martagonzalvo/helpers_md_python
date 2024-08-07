# File with various helper functions to evaluate guide RNAs.

import matplotlib.pyplot as plt
import nupack

def complement(seq):
    '''Calculates complement sequence to nucleic acid, 
    works for RNA and DNA
    Input: string  
    Example:
      complement('AATTC') ->
        'AATTC+GAATT' '''
    compls = {'A':'T', 'T':'A', 'C':'G', 'G':'C', 'd': '', 'U': 'A'}

    compl = ''
    for s in seq:
        compl+=compls[s]
    return seq+'+'+compl[::-1] 

def dotparen_stem(seq):
    '''Calculates dot-parens notation structure of nucleic acid
    sequence + it's compliment.
    Input: string of single strand
    Example:
        dotparen_stem('AATTC') ->
        '(((((+)))))' '''

    length = len(seq)

    return '('*length+'+'+')'*length

def nupack_energy_stem(strand1, material='RNA'):
    ''' Calculates energy of secondary structure: stem of strand
    with its complement. 

    Input: 
        strand1: string of single strand
        material: string 'RNA' or 'DNA'
    Output:
        Float of units kJ/mol'''
    both = complement(strand1)
    strand2 = both.split('+')[1]

    struct = dotparen_stem(strand1)
    model = nupack.Model(material=material)

    energy_stem = nupack.structure_energy(strands=[strand1, strand2], structure=struct, model=model)

    return energy_stem

def plot_energies_seqs(trnaseq, names, good_splicing, title):
    '''Will plot energies of rna sequence with it's complement as a bar plot.
    Inputs:
        trnaseq: 
            is list of guides or corresponding trna sequences.
            list of strings of sequences
        names: 
            list of names of the trnaseq list elements for plot labels
            list of strings
        good_splicing:
            list of names or sequences of guides to highlight, generate good cleavage
            list of strings
        title:
            title for plot
            string
    '''

    for seq, name in zip(trnaseq, names):
        energy_stem = nupack_energy_stem(seq)
        if seq in good_splicing or name in good_splicing:
            plt.bar(name, energy_stem, color='orange')
            continue
        else:
            plt.bar(name, energy_stem, color='black')

    
    plt.ylabel('Energy structure bound (kJ/mol)')
    plt.title(title)

    plt.xticks(fontsize=8, rotation=45)
    plt.show()

def generate_guides(fulltrnaseq, length_guides):
    '''Generates complements to all possible guides for a given 
     trna or other nucleic acid sequence
    Inputs:
        - fulltrnaseq: string of sequence of trna of interest
        - length_guides: integer
    Outputs:
        - list of strings of possible guide-binding regions 
        (not actual guide sequences)'''
    possible_guides = []
    starting = fulltrnaseq[:length_guides]
    possible_guides.append(starting)

    previous = starting
    for base in fulltrnaseq[length_guides:]:
        new = previous[1:]+base
        possible_guides.append(new)
        previous=new
    return possible_guides

def plot_energies_allguides(title, fulltrnaseq, length_guides, good_guides=None):

    ''' 
    Inputs:
        - fulltrnaseq: string of sequence of trna of interest
        - length_guides: integer
        - good_guides: sequences of guides to highlight in plot
        - title: string, title for plot
    '''

    possible_guides = generate_guides(fulltrnaseq, length_guides)
    names_newguides = [str(i) for i in range(len(possible_guides))]

    if not good_guides:
        good_guides = ['']

    plot_energies_seqs(possible_guides,  names_newguides, good_guides, title)
