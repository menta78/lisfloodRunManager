#!/bin/bash

var=$1
echo 'generating variable '$var

py=/STORAGE/usr/anaconda2/bin/python
$py generateMergedOutput.py /DATA/JEODPP/eos/projects/CRITECH/ADAPTATION/ClimateRuns/LisfloodEuroCordex/ /H01_Fresh_Water_Archive/Europe/Peseta4/LisfloodEuroCordex/ $1
