#!/bin/bash

# Source the export script
#source /home/anuarrozman/esp/esp-idf/export.sh
source /usr/src/app/esp/esp-idf/export.sh

# Print a message to indicate the script has been sourced
echo "ESP-IDF environment has been set up."

python3 main.py
