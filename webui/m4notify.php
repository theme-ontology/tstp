<?php
$name = $_GET["name"];
$url = NULL;
if($name == "gitupdate") 
{
    $url = "http://127.0.0.1:31985/event/gitchanged";
}
if($name == "validate") 
{
    $url = "http://127.0.0.1:31985/task/validate";
}
if($name == "monitorgit") 
{
    $url = "http://127.0.0.1:31985/task/monitorgit";
}
if ($url) {
    $response = file_get_contents($url);
}
?>
[<?php echo $_GET["name"]; ?>]
