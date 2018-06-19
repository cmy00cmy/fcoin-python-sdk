#! /bin/sh
pid=`ps -ef|grep python3|grep PWOS|awk '{print $2}'`
echo "PWOS $pid"
kill -9 $pid
wdid=`ps -ef|grep python3|grep watchdog|awk '{print $2}'`
echo "PWOS $wdid"
kill -9 $wdid
#python3 PWOS.py >> PWOS.log &
