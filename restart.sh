#! /bin/sh
ID=`ps -ef|grep python3|grep PWOS|awk '{print $2}'`
kill -9 $ID
echo "kill $ID"
nohup python3 PWOS.py &
nID=`ps -ef|grep python3|grep PWOS|awk '{print $2}'`
echo "start program, PID:$nID"
