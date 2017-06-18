<?php
header('Content-Type: application/json');
require_once("preamble.php");
require_once("pythonlib.php");
chdir("../pylib");
echo tstp_run_python('python -m webvizdata');
?>
