#Job Universe
#niverse = vanilla
universe  = docker
docker_image = critech_debian:1.0

confDir='@CONF_DIR@'
logFile="$confDir/runAll.log"

environment = "LF_INIT_FILE=$confDir/init.pkl LF_LOG_FILE=$logFile"

#script or executable
executable   = '@EXECUTABLE@'
request_cpus = 5

#Standar outputs
Output = @CONF_DIR@/condor_job.$(Cluster)_$(Process).out
Error = @CONF_DIR@/condor_job.$(Cluster)_$(Process).err
Log = @CONF_DIR@/condor_job.$(Cluster)_$(Process).log

queue 

