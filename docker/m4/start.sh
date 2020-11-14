#!/bin/sh

# only m-4 should be doing this bit
/build/docker/tstpconfig.sh
while ! nc -z mysql 3306; do echo "waiting on mysql:3306..."; sleep 3; done
/code/tstp/scripts/run python /code/tstp/pylib/dbdefine.py assertall -q
/code/tstp/scripts/pyrun m4.server

