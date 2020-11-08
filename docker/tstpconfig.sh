#!/bin/sh

FILE=/local/tstp

if [ -d "$FILE" ]; then
    echo "configuring for: UAT"
    ln -s /local/tstp /code/tstp
else
    echo "configuring for: PROD"
    echo "..."
fi


