#!/bin/sh

set -e
set -x

if [ ! -f /home/bnc/.znc/znc.conf ]
then
    echo "Could not find ZNC config file, installing new one"
    mkdir /home/bnc/.znc/configs -p
    cp /orig/* /home/bnc/.znc/configs
fi

exec znc -f
