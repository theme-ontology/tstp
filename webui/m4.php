<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Theme Ontology M-4 Themeontolonic Assistant</title>
<?php include "header.php"; ?>
</head>

<body>
<?php include "navbar.php"; ?>

<?php
    $url = "http://127.0.0.1:31985/status";
    $m4status = file_get_contents($url);
    $m4status = json_decode($m4status);
?>

<div class="container main-body">
    <div class="row">
        <div id="div_m4status" class="col-md-12 hpad0">
            <div class="basebox">
                <H4>The M-4 Themeontolonic Assistant</H4>

<?php
foreach ($m4status->subtasks as &$task)
{
    $s = $task->status[1];
    $t = $task->status[0];
    if ($s === "unknown") { 
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

                <BR>
                <H5>M-4 status is:</H5>
                <pre><?php echo htmlentities($m4status->m4log); ?></pre>
                <P><A href="/pub/m4/">browse all m4 information</A></P>
            </div>

        </div>
    </div>
</div>


<?php include "footer.php"; ?>

</body>
</html>
