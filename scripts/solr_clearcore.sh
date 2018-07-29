#!/bin/bash

/usr/local/solr/bin/post -c tstp -type text/xml -out yes -d $'<delete><query>*:*</query></delete>'
