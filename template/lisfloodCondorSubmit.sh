#Job Universe
#niverse = vanilla
universe  = docker
docker_image = critech_debian:1.0

environment = "LF_INIT_FILE=@CONF_DIR@/init.pkl LF_LOG_FILE=@CONF_DIR@/runAll.log"

#script or executable
executable   = @EXECUTABLE@
+Owner="critechproc"

RequestCpus = 8
RequestMemory = 10Gb

#Standar outputs
#Output = @CONF_DIR@/condor_job.$(Cluster)_$(Process).out
#Error = @CONF_DIR@/condor_job.$(Cluster)_$(Process).err
#Log = @CONF_DIR@/condor_job.$(Cluster)_$(Process).log
Output =/eos/jeodpp/htcondor/processing_logs/CRITECH/lisflood/job_@JOB_TAG@_$(Cluster)_$(Process).out
Error = /eos/jeodpp/htcondor/processing_logs/CRITECH/lisflood/job_@JOB_TAG@_$(Cluster)_$(Process).err
Log = /eos/jeodpp/htcondor/processing_logs/CRITECH/lisflood/job_@JOB_TAG@_$(Cluster)_$(Process).log


queue 

