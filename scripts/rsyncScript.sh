#!/bin/bash



BASE_PATH=/usr/src/app/ATSoftwareDevelopmentTool
TARGET_PATH=/usr/src/app/ATSoftwareDevelopmentTool
SERVER_IP="175.139.179.193"
SERVER_USERNAME="syamsul"

rsync -avz -e 'ssh -p 2222' $BASE_PATH/ $SERVER_USERNAME@$SERVER_IP:$BASE_PATH/
