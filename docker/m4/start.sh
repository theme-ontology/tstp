#!/bin/sh

# only m-4 should be doing this
/build/docker/tstpconfig.sh
/wait
/code/tstp/scripts/run python /code/tstp/pylib/dbdefine.py
/code/tstp/scripts/pyrun m4.server

