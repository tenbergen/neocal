#!/bin/bash

if [ $EUID > 0 ]
   then echo "Please run with sudo. Exiting."
   exit
fi

echo "Updating system and installing required software..."
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install -y python3-pip
echo "   done."

echo "Installing required modules..."
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel astral
echo "   done."

echo "Setting up neocal service..."
sudo cp neocal.service /etc/systemd/system/neocal.service
sudo systemctl enable neocal.service
echo "   done."

echo "Starting neocal..."
sudo systemctl start neocal.service
echo "   installation complete."
