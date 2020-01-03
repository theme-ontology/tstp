# TSTP

http://www.themeontology.com/


## Overview

This repository contains tools and information relating to the theme ontology data defined at https://github.com/odinlake/theming. Look at that repository to understand background and definitions.


## Installation Notes

This package requires a LAMP server, i.e., Linux, Apache, MySQL, and PHP. It also requires Python 2.7 with suitable bindings.
Examples Apache config (the last RewriteRule is important):

```
<VirtualHost *:80>
    Alias /pub/ /var/www/pub/
    Alias /pub /var/www/pub
    DocumentRoot /var/www/html/tstp/webui
    ServerName www.themeontology.org
    ServerAlias themeontology.org
    RewriteEngine on
    RewriteCond %{SERVER_NAME} =themeontology.org [OR]
    RewriteCond %{SERVER_NAME} =www.themeontology.org
    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_URI} /[^\./]*$
    RewriteRule (.*) $1.php [L]
</VirtualHost>
```

For MySQL, see pylib/credentials_template.py. A suitable database and user/password must be created and then configured there.
For the search function to work, Apache Solr is needed. 


