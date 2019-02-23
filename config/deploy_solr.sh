#!/bin/bash

sudo -u solr cp /var/solr/data/tstptheme/conf/solrconfig.xml /tmp/backup_tstptheme_solrconfig.xml
sudo -u solr cp tstp_solrconfig.xml /var/solr/data/tstptheme/conf/solrconfig.xml
cp /tmp/backup_tstptheme_solrconfig.xml backup_tstptheme_solrconfig.xml
sudo service solr restart



