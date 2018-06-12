#! /bin/sh
ID=`ps -ef|grep python3|grep PWOS|awk '{print $2}'`
echo $ID
kill -9 $ID
#python3 PWOS.py >> PWOS.log &
