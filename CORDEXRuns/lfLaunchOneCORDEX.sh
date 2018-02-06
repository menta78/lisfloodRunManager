#!/bin/bash
echo "launching lisflood!!"
logFile=$LF_LOG_FILE
echo $logFile

source /eos/jeodpp/data/projects/CRITECH/miniconda3/envs/LISFLOOD/bin/activate LISFLOOD

python /eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/CORDEXRuns/lfLaunchOneCORDEX.py > $logFile 2>&1

