# Script that runs bash script and prints how long does it take to run 
# usage python timing_bash.py bashscripttorun.sh
import sys, subprocess, time

start = time.time()
script = str(sys.argv[1])

subprocess.call('bash %s'%script, shell=True)
runtime = time.time()-start
runtime_min = runtime/60
print('script took %d minutes to run'%runtime_min)
