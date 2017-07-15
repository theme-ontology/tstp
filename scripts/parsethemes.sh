#!/bin/bash

# Make sure only ec2-user can run script
if [ "$(id -u)" != "500" ]; then
   echo "This script must be run as ec2-user" 1>&2
   exit 1
fi

cd ~/dev/themes
git pull
pyrun -m parsethemes .


