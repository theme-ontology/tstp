<?php 
require_once("preamble.php");
require_once("pythonlib.php");
$ret = tstp_run_python('python ../pylib/webdownload.py');

if ($ret[0] == "<") {
	echo $ret;
} else {
	header('Content-Type: text/csv');
	header('Content-Disposition: attachment; filename="data.csv";');
	echo $ret;
}

?>