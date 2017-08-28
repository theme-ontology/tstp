<?php

$legacy_setup_done = false;

function legacy_setup() {
    global $legacy_setup_done;

    if (!$legacy_setup_done) {
        $legacy_setup_done = true;

        $DIR_LOCATIONS = array( 
            "F:\Workspace\PyTrekTools",
            "/home/odinlake/tstpdm/scripts/lib/python2.6/site-packages/",
        );

        $pp = getenv("PYTHONPATH");

        if ($pp === FALSE) $pp = "";
        else $pp += ";";

        foreach ($DIR_LOCATIONS as $dir)
        {
            if (file_exists($dir))
            {
                putenv("PYTHONPATH=$pp$dir");
                break;
            }
        }
    }
}


// put back server variables!
foreach($_SERVER as $key => $value)
{
	if (is_string($value))
	{
		putenv("$key=$value");
	}
}


function tstp_run_python($cmd) {
    legacy_setup();
    
	$fn = "";

	// note: OS/Apache interferes with stdin PIPE when using proc_open
	// thus this daft file writing hack

	$payload = array(
		"FILES" => $_FILES,
		"POST" => $_POST,
		"GET" => $_GET,
		"PHP_SESSION_ID" => session_id(),
	);

	$fn = tempnam('/tmp', 'jsonphp_');
	$f = fopen($fn, 'w+');
	if ($f) fwrite($f, json_encode($payload));
	fclose($f);
	$cmd .= " ".$fn;

	$fd = popen($cmd, "r");
	$result = stream_get_contents($fd);

	fclose($fd);
	if ($fn) unlink($fn);
	ob_flush();

	return $result;
}


function tstp_simple_run($cmd) {
    $fd = popen($cmd, "r");
    $result = stream_get_contents($fd);
    fclose($fd);
    return $result;
}


function tstp_basedir() {
    $s = "tstp";
    $n = strlen($s);
    $d = "";
    do {
        $pd = $d;
        $d = rtrim(getcwd(), "\\/");
        if (substr($d, -$n) === $s) break;
        else chdir("..");
    } while ($pd != $d);
    return getcwd();
}


function tstp_pyrun($cmd) {
    $cmd = tstp_basedir() . '/scripts/pyrun ' . $cmd;
    $fd = popen($cmd, "r");
    $result = stream_get_contents($fd);
    fclose($fd);
    return $result;
}

?>