# Corrects HILLs files by deleting additional headers and deletes additional headers 
# Usually needed when node crashed and simulation was restarted
# usage: python fix_restart_hills.py HILLSfile newfilename

# ASSUMES HILLS has 4 header lines at the beginning


import os, sys

tomod = sys.argv[1]
newfile = sys.argv[2]

with open(str(tomod)) as f:
    newlines = []
    validlines = 0
    numrestarts = 0
    lines = f.readlines()

    for i, line in enumerate(lines):

        # always include first header in first 4 lines
        if i < 4:
            newlines.append(line)
            continue
        
        # 'delete' restart headers - don't include
        if "#!" in line:
            numrestarts += 1
            continue
        
        else: 
            # hills starts on 1, colvar on 0
            validlines += 1
            # create new line with right timestep + rest of line 
            newline = '      '+str(validlines)+'.0 '+line[24:]#+'\n'
            newlines.append(newline)
            
    # check number of lines
    assert len(newlines) == validlines + 4, 'newlines wrong' # initial line
    assert i + 1 == numrestarts + validlines + 4, 'i not restart+validlines' # i is 0-indexed

# Saving into new file
with open(str(newfile), "w") as f:
    f.writelines(newlines)
print()
print('SUMMARY OF CHANGES')
print()
print(str(tomod), '----->', str(newfile))
print()
print('Deleted header lines (re-starts) (individual lines, not number of restarts) ', numrestarts)
print('Original file had this many lines', i+1)
print('New file has this many lines', len(newlines))


