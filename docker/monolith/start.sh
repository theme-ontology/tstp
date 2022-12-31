#!/bin/sh

# only m-4 should be doing this bit
/build/docker/tstpconfig.sh
while ! nc -z mysql 3306; do echo "waiting on mysql:3306..."; sleep 3; done

set +e
/code/tstp/scripts/run python /code/tstp/pylib/dbdefine.py assertall -q
while true; do
    /code/tstp/scripts/pyrun m4.server;
    echo "M-4 exited, waiting 3s to restart..."
    sleep 3
done
