<?php
header('Content-Type: application/json');
require_once("preamble.php");
require_once("pythonlib.php");

if (!getenv("TSTPDOCKER")) {
    echo tstp_run_python('python ../pylib/webquery.py');
} else {
    $url = "http://m4:31985/webjson?" . $_SERVER['QUERY_STRING'];
    echo file_get_contents($url);
}
?>