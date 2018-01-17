#Job Universe
#niverse = vanilla
universe  = docker
docker_image = critech_debian:1.0

environment = "TESTVARIABLE1=test1 TESTVARIABLE2=test2"

#script or executable
executable     = /eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/test/testLaunchJeodpp.sh
request_cpus = 5

#Standar outputs
Output =/eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/test/log/$(Cluster)_$(Process).out
Error = /eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/test/log/$(Cluster)_$(Process).err
Log = /eos/jeodpp/data/projects/CRITECH/ADAPTATION/src/git/lisfloodRunManager/test/log/$(Cluster)_$(Process).log




queue 

