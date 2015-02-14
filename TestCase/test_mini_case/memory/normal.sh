#!/bin/sh

workdir=/data/local/tmp/memory
workout=${workdir}/out

dumpsys meminfo > ${workout}/meminfo-2.txt
