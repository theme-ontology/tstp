<?php 
require_once("preamble.php");
require_once("pythonlib.php");
$ret = tstp_run_python('python ../pylib/webdownload.py');

if ($ret[0] == "<") {
    echo $ret;
} else {
    if ($_GET["fmt"] == "xls")
    {
        //$file = str_replace("\\", "/", $ret);
        //$file = str_replace("//", "/", $file);
        //echo $file."<br>";
        //$file = "c:/windows/temp/b91ab3649e/userstorythemes.xls";
        //echo $file."<br>";
        $file = trim($ret);

        header('Content-Description: File Transfer');
        header('Content-Type: application/vnd.ms-excel');
        header('Content-Disposition: attachment; filename="data.xls";');
        header('Content-Transfer-Encoding: binary');
        header('Content-Length: ' . filesize($file));
        readfile($file);

    } else {
        header('Content-Type: text/csv');
        header('Content-Disposition: attachment; filename="data.csv";');
    }
}

?>