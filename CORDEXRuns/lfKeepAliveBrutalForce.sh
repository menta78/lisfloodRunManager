#!/bin/bash

curdir=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
echo "current directory: "$curdir

while true
do
  echo 'removing possible hang jobs'
  condor_q | grep lf | grep H | awk '{print $1}' | xargs condor_rm
  echo 'sleeping a couple of minutes'
  sleep 120
  echo 'resubmitting dead jobs'
  python lfLaunchAllCORDEX.py
  echo 'sleeping for 1 hour'
  sleep 3600
done

