#! /bin/sh
ID=`ps -ef|grep python3|grep PWOS|awk '{print $2}'`
kill -9 $ID
echo "kill $ID"
python3 PWOS.py >> PWOS.log &
nID=`ps -ef|grep python3|grep PWOS|awk '{print $2}'`
echo "start program, PID:$nID"
