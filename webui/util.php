<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Theme Ontology util</title>
<?php include "header.php"; ?>
    <script>
        var TASKSTATE = "unknown";
        var QUERYPENDING = false;
        var LOADTIME = 0;

        function scrollToBottom(name) 
        {
            var element = document.getElementById(name);
            element.scrollTop = element.scrollHeight;
        }
        function updateButtonStatus()
        {
            var val = $('#fieldVerify').is(':checked');
            $('#commitbutton').attr("disabled", !val);
        }
        function updateM4Status(taskname)
        {
            if (!QUERYPENDING)
            {
                QUERYPENDING = true;
                $.getJSON("m4status.php", function(result) {
                    QUERYPENDING = false;
                    $.each(result["subtasks"], function(i, subtask) {
                        if (subtask.shortname == taskname)
                        {
                            if (subtask.running) {
                                TASKSTATE = "started";
                                alertType = "info";
                            } else if (TASKSTATE == "started") {
                                TASKSTATE = "finished";
                                alertType = "success";
                            } else if (TASKSTATE != "finished") {
                                timeout = Math.round((LOADTIME + 20000 - Date.now()) / 1000);
                                if (timeout > 0)
                                    TASKSTATE = "waiting " + timeout + "s to start...";
                                else
                                    TASKSTATE = "M-4 not responding...";
                                alertType = "warning";
                            }
                            elem = $("#m4status");
                            pclass = elem.attr('class').split(' ').pop();
                            elem.removeClass(pclass);
                            elem.addClass("alert-" + alertType);
                            elem.text("M-4 Task status is: " + TASKSTATE);
                            if (TASKSTATE == "started" || TASKSTATE == "finished")
                            {
                                QUERYPENDING = true;
                                $.get(subtask.logpath, function(result) {
                                    QUERYPENDING = false;
                                    var element = document.getElementById("m4log");
                                    $("#m4log").text(result);
                                    scrollToBottom("m4log");
                                });
                            }
                        }
                    });
                });
            }
            if (TASKSTATE != "finished")
                setTimeout(() => { updateM4Status(taskname); }, 1000);
        }

    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container">
<?php
    $submit = $_POST["submit"];
    $action = $_POST["action"];
    $response = "";
    $result = "";
    $showM4task = "";

    if($submit == "commit") {
        require_once("pythonlib.php");

        if ($action == "runtests")
        {
            $out = tstp_pyrun('webtask.test_formatting 2>&1');
            echo "<h1>webtask.test_formatting</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.test_integrity 2>&1');
            echo "<h1>webtask.test_integrity</h1><pre>" . htmlentities($out) . "</pre>\n";
        }
        elseif ($action == "importgit-old")
        {
            $out = tstp_pyrun('webtask.updaterepo 2>&1');
            echo "<h1>webtask.updaterepo</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.importgit 2>&1');
            echo "<h1>webtask.importgit</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.cache_queries 2>&1');
            echo "<h1>webtask.cache_queries</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.maintenance 2>&1');
            echo "<h1>webtask.maintenance</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.test_integrity 2>&1');
            echo "<h1>webtask.test_integrity</h1><pre>" . htmlentities($out) . "</pre>\n";
        }
        elseif ($action == "importgit-new")
        {
            $target = explode("-", $action)[0];
            $url = "http://127.0.0.1:31985/task/" . $target;
            $response = file_get_contents($url);
            $showM4task = "importgit";
?>
<script>
    LOADTIME = Date.now();
    setTimeout(() => { updateM4Status("importgit"); }, 1000);
</script>
<?php
        }
    }

    if ($showM4task == "importgit") {
?>
    <div class="row">
        <div class="basebox">
            <div id="m4status" class="alert alert-danger" role="alert">waiting to start...</div>
            <pre id="m4log" style="overflow:auto; max-height:500px;">...</pre>
            <P><A href="/pub/m4/">browse all m4 information</A></P>
        </div>
    </div>
<?php
    }
?>
    <div class="row">
        <div class="col-md-6">
            <div class="basebox">
                Admin utilities.
            </div>
        </div>
        <div class="col-md-6">
            <div class="alert alert-info">
                <form method="post" enctype="multipart/form-data">
                    <fieldset class="form-group">
                        <label for="action">What?</label>
                        <select id="action" name="action">
                            <option value="nothing">&lt;nothing selected&gt;</option>
                            <option value="importgit-old">Old import data from GIT repository "theming/notes".</option>
                            <option value="importgit-new">Schedule GIT "theming/notes" import pipeline with M-4.</option>
                            <option value="runtests">Run tests on GIT repository "theming/notes".</option>
                        </select>
                    </fieldset>

                    <fieldset class="form-group">
                        <input id="fieldVerify" type="checkbox" OnChange="updateButtonStatus()">
                        <label for="fieldVerify">Are you sure you want to execute this function?</label>
                    </fieldset>

                    <button id="commitbutton" type="submit" name="submit" value="commit" class="btn btn-primary" disabled>Do It!</button>
                    <button type="submit" name="submit" value="cancel" class="btn btn-danger">Cancel</button>
                </form>
            </div>
        </div>
    </div>


</div>


<?php include "footer.php"; ?>

</body>
</html>
