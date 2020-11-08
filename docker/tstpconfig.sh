#!/bin/sh

FILE=/local/tstp
export TSTPDOCKER=1

if [ -d "$FILE" ]; then
    echo "configuring for: UAT"
    ln -s /local/tstp /code/tstp
    #cp -r /local/tstp /code/tstp
    #chown -R root:www-data /code/tstp
    #chmod -R 664 /code/tstp
    #chmod -R 774 /code/tstp/scripts
    #find /code/tstp -type d -exec chmod 775 {} \;
else
    echo "configuring for: PROD"
    echo "..."
fi


