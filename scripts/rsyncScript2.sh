#!/bin/bash

BASE_PATH=/usr/src/app/ATSoftwareDevelopmentTool
TARGET_PATH=/usr/src/app/ATSoftwareDevelopmentTool1

# get server name
SERVER=$1

# options
echo "Supply the server name when run."
echo "Example: bash rsyncScript2.sh <server name below>"
echo "Available server options:"
echo "neo-1"
echo "neo-2"
echo "testserver"

# exit if no server define
if [[ -z "$SERVER" ]]; then
    echo "Please supply a server name. Example: bash rsyncScript2.sh neo-1"
    exit 1
fi

case $SERVER in
    neo-1)
        echo "Rsync to $SERVER"
        SERVER_IP="100.113.142.62"
        rsync -avz --exclude 'device.txt' $BASE_PATH/ $SERVER_IP:$TARGET_PATH/
        ;;
    neo-2)
        echo "Rsync to $SERVER"
        echo "no command yet"
        ;;
    testserver)
        echo "Rsync to $SERVER"
        SERVER_IP="175.139.179.193"
        rsync -avz --exclude 'device.txt' $BASE_PATH/ $SERVER_IP:$TARGET_PATH/
        ;;
    *)
        echo "Unknown server: $SERVER"
        exit 1
        ;;
esac
