#!/bin/bash

source /etc/profile

####################### Configurations #######################
proj_dir=/root/fcoin-python-sdk
sudo_pass=j3QvMvNMkah2
sleepTime=60
##############################################################

log_dir=$proj_dir/logs/watchdog

if [ ! -d $log_dir ];then
    mkdir $log_dir
fi

log_file=$log_dir/$(date +"%Y-%m-%d")".log"

function log_sms()
{
    time=$(date +"%Y-%m-%d %H:%M:%S")
    write_str="$time $* not running, restarting..."
    echo $write_str >> $log_file
}

function pwos()
{
    process=`ps -ef |grep python3 | grep PWOS.py | grep -v grep | wc -l`
    if [ $process -eq 0 ];then
        log_sms process
        cd $proj_dir
        ./start.sh
    fi
}

while true; do
	pwos
	sleep $sleepTime
done

# ###
# ### locate_engine
# ###
# locate_engine_res=`ps aux | grep eg.jar | grep -v grep | wc -l`
# if [ $locate_engine_res -eq 0 ];then
#     log_sms locate_engine_res
#     locate_engine_res_conflict_pid=`netstat -anp | grep 26101 |  grep -v grep | awk '{print $7}' | cut -d/ -f1`
#     if [ $locate_engine_res_conflict_pid ];then
#         kill -9 $locate_engine_res_conflict_pid
#     fi
#     cd $install_dir/locate/run
#     ./shutdownengine.sh
#     sleep 1
#     ./startengine.sh
# fi


