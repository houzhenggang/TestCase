#!/bin/sh

if [ $1 == 'start' ] ;then
    $2/busybox nohup sh $2/start.sh $2 $3
elif [ $1 == 'wait' ] ;then
    sh $2/wait.sh $2 $3
elif [ $1 == 'exit' ] ;then
    sh $2/exit.sh $2 $3
fi
