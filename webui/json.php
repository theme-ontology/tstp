<?php
header('Content-Type: application/json');
require_once("preamble.php");
require_once("pythonlib.php");
echo tstp_run_python('python ../pylib/webquery.py');
?>