#!/bin/bash

#update system
sudo apt-get update && sudo apt-get upgrade -y

# Define the file path for the udev rules
rules_file="/etc/udev/rules.d/99-usb-serial.rules"

# Create or edit the udev rules file
sudo nano "$rules_file" << EOF
SUBSYSTEMS=="usb", MODE="0666"
EOF

# Reload the udev rules
sudo udevadm control --reload-rules

# Install esptool
pip install esptool --break-system-packages

# Install pyinstaller
pip install pyinstaller --break-system-packages

# Install hidapi
pip install hidapi --break-system-packages

# Install hid
pip install hid --break-system-packages

export ProdTool_Path=${HOME}/ATSoftwareDevelopmentTool/Sprint14-Prototype/

# Build the project
pyinstaller --onefile main.py --hidden-import esptool --hidden-import pyserial --hidden-import hidapi --hidden-import hid --distpath ${ProdTool_Path}

