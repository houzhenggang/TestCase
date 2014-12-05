#!/bin/sh

dd if=/dev/zero of=/data/local/tmp/fat_test.bin bs=4k count=131072
cp /data/local/tmp/fat_test.bin /dev
echo /dev/fat_test.bin > sys/class/android_usb/f_mass_storage/lun/file
