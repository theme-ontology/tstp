<?php
header('Content-Type: application/json');
require_once("preamble.php");
require_once("pythonlib.php");

if ($_SESSION["isHuman"] === true)
{
    echo tstp_run_python('python ../pylib/websubmit.py');
} else {
    echo '{"error":"You must be logged in or verified to use this function."}';
}

?>