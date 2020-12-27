<?php

// lifted from
// https://stackoverflow.com/questions/5647461/how-do-i-send-a-post-request-with-php
function post_request($url, array $params) {
    $query_content = http_build_query($params);
    $fp = fopen($url, 'r', FALSE,
        stream_context_create([
        'http' => [
            'header'  => [
                'Content-type: application/x-www-form-urlencoded',
                'Content-Length: ' . strlen($query_content)
            ],
            'method'  => 'POST',
            'content' => $query_content
        ]
    ]));
    if ($fp === FALSE) {
        return json_encode(['error' => 'Failed to get contents...']);
    }
    $result = stream_get_contents($fp);
    fclose($fp);
    return $result;
}


// simple get queries recognized
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
if($name == "buildanimation") 
{
    $url = "http://127.0.0.1:31985/task/buildanimation";
}
/* disabled for safety
if($name == "importgit") 
{
    $url = "http://127.0.0.1:31985/task/importgit";
}
*/
if ($url) {
    $response = file_get_contents($url);
    echo "[" . $_GET["name"] . "]\n";
}

// more complex post queries
if($name == "gitsearch") 
{
    header('Content-Type: application/json');
    $url = "http://127.0.0.1:31985/tool/gitsearch";
    $params = array(
        'query' => $_GET["query"]
    );
    $response  = post_request($url, $params);
    echo $response;
    echo " ";
}
?>
