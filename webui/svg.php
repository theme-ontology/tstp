<?php
header('Content-Type: image/svg+xml');
require_once("preamble.php");
require_once("pythonlib.php");
chdir("../pylib");
echo tstp_run_python('python -m viz.themecube');
?>
