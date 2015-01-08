#!/bin/sh

workdir=/data/local/tmp/scenes
workout=${workdir}/out
mkdir -p ${workout}

${workdir}/busybox nohup sh ${workdir}/scenes.sh
