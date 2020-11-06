#!/bin/bash

# Connect to the wifi
# connmanctl enable wifi
# connmanctl agent on
# connmanctl connect <wifi>

#set up symbolic link

echo temppwd | sudo -S ln -s /dev/spidev1.0 /dev/spidev0.0

# Change to appropriate directory
cd /var/lib/cloud9/ENGI301/Project

# Runs the code to display

PYTHONPATH=/var/lib/cloud9/ENGI301/Project python3 main.py
