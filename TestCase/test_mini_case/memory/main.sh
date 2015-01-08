#!/bin/sh

workdir=/data/local/tmp/memory
workout=${workdir}/out
mkdir -p ${workout}

${workdir}/busybox nohup sh ${workdir}/memory.sh
