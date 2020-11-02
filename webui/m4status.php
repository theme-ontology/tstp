<?php
    header('Content-Type: application/json');
    require_once("preamble.php");
    require_once("pythonlib.php");
    $url = "http://127.0.0.1:31985/status";
    $m4status = file_get_contents($url);
    $m4status = json_decode($m4status);
    if ($m4status == NULL) {
        $m4status = (object) [
            "m4log" => "<empty>\n",
            "status" => "NOT RESPONDING",
            "subtasks" => [],
        ];
    }
    echo json_encode($m4status);
?>