<?php 
require_once("preamble.php");
require_once("pythonlib.php");
$ret = tstp_run_python('python ../pylib/webdownload.py');

if ($ret[0] == "<") {
    echo $ret;
} else {
    $what = $_GET["what"];

    if ($_GET["fmt"] == "xls")
    {
        $file = trim($ret);

        header('Content-Description: File Transfer');
        header('Content-Type: application/vnd.ms-excel');
        header('Content-Disposition: attachment; filename="'.$what.'.xls";');
        header('Content-Transfer-Encoding: binary');
        header('Content-Length: ' . filesize($file));
        readfile($file);

    } else if ($_GET["fmt"] == "txt") {
        header('Content-Type: text/plain; charset=utf-8');
        header('Content-Disposition: attachment; filename="'.$what.'.txt";');
        echo $ret;

    } else {
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="'.$what.'.csv";');
        echo $ret;
    }
}

?>