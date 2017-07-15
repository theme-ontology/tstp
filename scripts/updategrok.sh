#!/bin/bash


# Make sure only ec2-user can run script
if [ "$(id -u)" != "500" ]; then
   echo "This script must be run as ec2-user" 1>&2
   exit 1
fi

cd ~/dev/tstp
if [[ $(git pull) != "Already up-to-date." ]]; then
    sudo /home/ec2-user/opengrok-1.1-rc3/bin/OpenGrok index /home/ec2-user/dev
fi

