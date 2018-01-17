#!/bin/bash

. /eos/jeodpp/data/projects/CRITECH/miniconda3/envs/LISFLOOD/bin/activate LISFLOOD

pythonScrpt=/eos/jeodpp/data/projects/CRITECH/miniconda3/envs/LISFLOOD/bin/python
scrptPth=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/test/testRun_Jeodpp.py
logPth=/eos/jeodpp/data/projects/CRITECH/ADAPTATION/lisflood/lisfloodRun/testEuropeRestartJRCAutomatic/run/master.log

$pythonScrpt $scrptPth > $logPth 2>&1

