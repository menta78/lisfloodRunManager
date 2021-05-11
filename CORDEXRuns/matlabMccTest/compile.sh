export LD_LIBRARY_PATH='/STORAGE/usr/MATLAB/R2017a/sys/os/glnxa64:/STORAGE/usr/MATLAB/R2017a/bin/glnxa64:/STORAGE/usr/MATLAB/R2017a/extern/lib/glnxa64:/STORAGE/usr/MATLAB/R2017a/runtime/glnxa64:/STORAGE/usr/MATLAB/R2017a/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:/STORAGE/usr/MATLAB/R2017a/sys/java/jre/glnxa64/jre/lib/amd64/server'

currPath=$PWD
/STORAGE/usr/MATLAB/R2017a/bin/mcc -m hpcTest.m -a /STORAGE/src1/git/tsEva -a $currPath -o lfRunTest

