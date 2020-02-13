<?php
if($_GET["name"] == "gitupdate") {
    $url = "http://127.0.0.1:31985/task/validate"
    $response = file_get_contents($url);
}
?>
[<?php echo $_GET["name"]; ?>]
