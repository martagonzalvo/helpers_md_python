# Corrects colvars file generated by plumed by deleting additional headers and deletes additional headers 
# Usually needed when node crashed and simulation was restarted
# usage: python fix_restart_colvar.py COLVAR_free newfilename

# ASSUMES colvar only has 1 header line


import os, sys

tomod = sys.argv[1]
newfile = sys.argv[2]

with open(str(tomod)) as f:
    newlines = []
    validlines = 0
    rightafterrestart = False
    numrestarts = 0
    skipped = 0
    lines = f.readlines()
    for i, line in enumerate(lines):
        
        # always include first header in first line
        if i == 0:
            newlines.append(line)
            continue

        # 'delete' restart headers - don't include
        if "#! FIELDS" in line:
            rightafterrestart = True
            numrestarts += 1
            continue

        # if line after a re-start is identical to the line before the
        # restart, do not include line in new file
        if rightafterrestart:
            rightafterrestart = False
            if line == lines[i-2]:
                skipped += 1
                continue

        # create new line with right timestep + rest of line 
        newline = str(validlines)+'.0 '+' '.join(line.split()[1:])+'\n'
        newlines.append(newline)
        # hills starts on 1, colvar on 0
        validlines += 1

    # check number of lines
    assert len(newlines) == validlines + 1, 'newlines wrong' # initial line
    assert i + 1 == numrestarts + skipped + validlines + 1, 'total lines not= restart+validlines'

# Saving into new file
with open(str(newfile), "w") as f:
    f.writelines(newlines)

print()
print('SUMMARY OF CHANGES')
print()
print(str(tomod), '----->', str(newfile))
print()
print('Deleted header lines (re-starts) ', numrestarts)
print('Deleted repeated lines after restarts ', skipped)
print('Original file had this many lines', i+1)
print('New file has this many lines', len(newlines))




