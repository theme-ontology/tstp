<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Theme Ontology M-4 Themeontolonic Assistant</title>
<?php include "header.php"; ?>

<script>
    function scrollToBottom(name) 
    {
        var element = document.getElementById(name);
        element.scrollTop = element.scrollHeight;
    }
</script>
</head>

<body onLoad="scrollToBottom('m4log');">
<?php include "navbar.php"; ?>

<?php
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
?>

<div class="container main-body">
    <div class="row">
        <div id="div_m4status" class="col-md-12 hpad0">
            <div class="basebox">
                <P><IMG src="img/icon-machine.svg" height="100px"></P>
                <H4>Welcome to The M-4 Themeontolonic Assistant</H4>
            </div>
            <div class="basebox">
                <H5>M-4 Tools</H5>
                    <A href="m4gitsearch">git-search</A>
            </div>
            <div class="basebox">
                <H5>M-4 Tasks</H5>
<?php
foreach ($m4status->subtasks as &$task)
{
    $s = $task->status[1];
    $t = $task->status[0];
    $r = $task->running;
    if ($t === "running") { 
        $alerttype = "info"; 
        $title = "task running";
    }
    elseif ($s === "unknown" || $r > 0) { 
        $alerttype = "warning"; 
        $title = "unknown status"; 
    }
    elseif ($s === 0) { 
        $alerttype = "success"; 
        $title = "task succeeded"; 
    }
    else { 
        $alerttype = "danger"; 
        $title = "task failed"; 
    }
?>
                <div class="alert alert-<?php echo $alerttype; ?>" role="alert">
                    <font color="black"><?php echo $task->name; ?></font>
                    <font><?php echo substr($t, 0, 19); ?></font>:
                    <?php echo $title; ?>, exit code <?php echo $s; ?>.
                    <div style="float:right;">
                        [<A target="_top" href="m4notify?name=<?php echo $task->shortname; ?>">ping</A>]
<?php
    if ($s === "unknown") {
?>
                        [<i>log</i>]
<?php
    } else {
?>
                        [<A href="<?php echo $task->logpath; ?>">log</A>]
<?php
    }
?>
                    </div>
                </div>

<?php
}
?>
            </div>
            <div class="basebox">
                <H5>M-4 status is <?php echo $m4status->status; ?>:</H5>
                <pre id="m4log"
                     style="overflow:auto; max-height:200px;" 
                ><?php 
                    echo htmlentities($m4status->m4log); 
                ?></pre>
                <P><A href="/pub/m4/">browse all m4 information</A></P>
            </div>

        </div>
    </div>
</div>


<?php include "footer.php"; ?>

</body>
</html>
