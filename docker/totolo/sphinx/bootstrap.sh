#!/bin/sh

# because Docker can't seem to overwrite sphinx.conf during build in-place if container is running
cp -f /sphinx/sphinx.conf /opt/sphinx/conf/sphinx.conf
# from parent image CMD
/bin/sh -c "searchd --nodetach --config /opt/sphinx/conf/sphinx.conf"
echo "sphinx defeated"
