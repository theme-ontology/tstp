<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>TSTP new story</title>
<?php include "header.php"; ?>

    <script>
        var scheduled = 0;
        var lastRequest = null;
        var metadata = null;
        var saved = {};

        function getSaved()
        {
            $.getJSON("json.php?action=protostory_saved", function(response) {
                console.log(response);
                var $el = $("#savedstories");
                $el.empty();
                $el.append($("<option></option>").attr("value", "").text(""));
                saved = {};
                for (var i=0; i<response.length; i++)
                {
                    var key = response[i][0];
                    saved[key] = response[i][1];
                    $el.append($("<option></option>").attr("value", key).text(key));
                }
            });
        }

        function scheduleReload()
        {
            scheduled += 1;
            setTimeout(postReload, 500);
        }

        function postReload()
        {
            scheduled -= 1;

            if (scheduled == 0)
            {
                var target_url = $("#importurl").val();
                var url = "json.php?action=urlimport&url=" + encodeURIComponent(target_url);
                if (lastRequest != target_url && target_url != "")
                {
                    lastRequest = target_url;
                    $.getJSON(url, function(response) {
                        console.info(response);
                        $("#savedstories").val("");

                        if ("title" in response && "year" in response)
                        {
                            metadata = response;
                            var sid = response["type"] + ": " + response['title'] + " (" + response["year"] + ")"
                            sid = sid.replace(/[^\w: ()]/g, ''); // no commas and percents in sid (are there other bad characters?)
                            $("#fieldSID").val(sid);
                            updateOutput();
                            $("#errorFieldSet").css('display', 'none');
                            $("#outputFieldSet").css('display', 'block');
                        }

                        if ("error" in response)
                        {
                            $("#errorFieldSet").css('display', 'block');
                            $("#outputFieldSet").css('display', 'none');
                            $("#fieldError").val(response["error"]);
                        }
                    });
                }
            }
        }

        function loadOutput()
        {
            var sel = $("#savedstories").val();
            if (sel in saved)
            {
                $("#importurl").val("");
                $("#fieldOutput").val(saved[sel]);
            }
        }

        // https://en.wikipedia.org/wiki/Robot_Monster
        function updateOutput()
        {
            var sid = $("#fieldSID").val();
            var out = sid + "\n" + "=".repeat(sid.length) + "\n\n";
            var fields = [
                ["title", metadata["title"]],
                ["description", metadata["description"]],
                ["date", metadata["date"]],
            ];

            if ($("#fieldRatings").prop('checked'))
                fields.push(["ratings", ""]);
            if ($("#fieldGenre").prop('checked'))
                fields.push(["genre", ""]);

            fields.push(["choice themes", ""]);
            fields.push(["major themes", ""]);
            fields.push(["minor themes", ""]);

            for(var i=0; i<fields.length; i++)
            {
                var fn = fields[i][0].replace(/^\w| \w/g, function (chr) {
                    return chr.toUpperCase();
                });
                out += ":: " + fn + "\n";
                out += fields[i][1] + "\n";

                if (fields[i][1].length)
                    out += "\n";
            }

            $("#fieldOutput").val(out);
        }

        function saveOutput()
        {
            var payload = {
                "action": "protostory",
                "storyentry": $("#fieldOutput").val(),
            };
            $.post( "submit", payload).done(function(response) {
                msg = Object.entries(response).map(x=>x.join(":")).join("\r\n");
                if ("error" in response)
                {
                    $("#message").css('display', 'none');
                    $("#error").text("Error: " + msg);
                    $("#error").css('display', 'block');
                } else {
                    $("#message").text("Saved! Response: " + msg);
                    $("#message").css('display', 'block');
                    $("#error").css('display', 'none');
                }
            });
        }

        function outputChanged()
        {
            if ($("#fieldOutput").val())
            {
                $("#message").text("(unsaved progress)");
                $("#message").css('display', 'block');
            } else {
                $("#message").css('display', 'none');
                $("#message").text("");
            }
        }

        getSaved();
    </script>
</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">

<?php // Basic information //?>
    <div class="row">
        <div class="col-md-12 hpad0">
            <fieldset class="form-group">
                <label for="importurl">Import from URL (copy&amp;paste Wikipedia link)</label>
                <input id="importurl" type="text" class="form-control" autofocus 
                    onchange="scheduleReload()" oninput="scheduleReload()">
            </fieldset>

            <fieldset class="form-group">
                <label for="savedstories">Or choose saved</label>
                <select id="savedstories" type="text" class="form-control"
                    onchange="loadOutput()" oninput="loadOutput()"></select>
            </fieldset>

            <fieldset class="form-group">
                <label for="fieldSID">Story ID</label>
                <input id="fieldSID" type="text" class="form-control" OnChange="updateOutput()">
            </fieldset>

            <fieldset class="form-group form-inline">
                <label for="fieldGenre" class="checkbox-inline">Genre</label>
                <input id="fieldGenre" type="checkbox" OnChange="updateOutput()">
                <label for="fieldRatings" class="checkbox-inline">Ratings</label>
                <input id="fieldRatings" type="checkbox" OnChange="updateOutput()">
            </fieldset>

            <fieldset id="errorFieldSet" class="form-group" style="display:none;">
                <label for="fieldError" style="color: #ff0000;">Errors</label>
                <textarea id="fieldError" class="form-control" style="font-family:monospace; background:#ffe8e0;" rows=25></textarea>
            </fieldset>

            <fieldset class="form-group">
                <label for="fieldOutput">Story Definition</label>
                <textarea id="fieldOutput" name="storyentry" class="form-control" style="font-family:monospace;" rows=25 OnChange="outputChanged()" OnKeyUp="outputChanged()"></textarea>
            </fieldset>
            <button id="commitbutton" OnClick="saveOutput();" class="btn btn-primary">
                save progress
            </button>
            <BR>
            &nbsp;
        </div>
    </div>
    <div class="row">
        <div class="col-md-12 hpad0">
            <div id="message" class="alert alert-info" style="display:none;"></div>
        </div>
        <div class="col-md-12 hpad0">
            <div id="error" class="alert alert-error" style="display:none;"></div>
        </div>
    </div>
</div>

<?php include "footer.php"; ?>
</body>
</html>
