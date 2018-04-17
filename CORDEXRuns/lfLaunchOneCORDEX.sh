#!/bin/bash
echo "launching lisflood!!"
logFile=$LF_LOG_FILE
echo $logFile

set -e

py=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/usr/anaconda_LISFLOOD/bin/python

$py /eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/CORDEXRuns/lfLaunchOneCORDEX.py > $logFile 2>&1

