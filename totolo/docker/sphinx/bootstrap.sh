#!/bin/sh

# because Docker can't seem to overwrite sphinx.conf during build in-place if container is running
cp -f /sphinx/sphinx.conf /opt/sphinx/conf/sphinx.conf

echo ":: STARTING UP AT PATH ::::::::::::::::::::::::::::::::::"
pwd
echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo ":: TOTOLO ENV :::::::::::::::::::::::::::::::::::::::::::"
env
echo ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::"

# from parent image CMD
/bin/sh -c "/opt/sphinx/sphinx-3.4.1/bin/searchd --nodetach --config /opt/sphinx/conf/sphinx.conf"  ## old version

echo "sphinx defeated"
