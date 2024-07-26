# Usage:

#   bash splitfilequartiles.sh filename

# Makes 3 copies of file filename with only 25%, 50% and 75% of lines

#!/bin/bash

NUMLINES=$(wc -l < $1)

# Getting slices HILLS files
FIRST=$((NUMLINES/4))
HALF=$((NUMLINES/2))
THIRD=$((NUMLINES*3/4))

#sed -n '1,$FIRSTp' $1 > $1_25p

cat $1 | head -$FIRST > $1_1quart
cat $1 | head -$HALF > $1_2quart
cat $1 | head -$THIRD > $1_3quart
