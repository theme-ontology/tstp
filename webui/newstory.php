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
                if (lastRequest != target_url)
                {
                    lastRequest = target_url;
                    $.getJSON(url, handleResponse);
                }
            }
        }

        function handleResponse(response)
        {
            console.info(response);

            if ("title" in response && "year" in response)
            {
                metadata = response;
                var sid = response["type"] + ": " + response['title'] + " (" + response["year"] + ")"
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
                var fn = fields[i][0].replace(/^\w/, function (chr) {
                    return chr.toUpperCase();
                });
                out += ":: " + fn + "\n";
                out += fields[i][1] + "\n";

                if (fields[i][1].length)
                    out += "\n";
            }

            $("#fieldOutput").val(out);
        }

    </script>
</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">

<?php // Basic information //?>
    <div class="row">
        <div class="col-md-12 hpad0">
                <form method="post" enctype="multipart/form-data">
                    <fieldset class="form-group">
                        <label for="importurl">Import from URL (copy&amp;paste Wikipedia link)</label>
                        <input id="importurl" type="text" class="form-control" autofocus 
                            onchange="scheduleReload()" oninput="scheduleReload()">
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
                </form>

                <form id="outputFieldSet" action="submit" method="post" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="protostory">
                    <fieldset class="form-group">
                        <label for="fieldOutput">Story Definition</label>
                        <textarea id="fieldOutput" name="storyentry" class="form-control" style="font-family:monospace;" rows=25></textarea>
                    </fieldset>
                    <button id="commitbutton" type="submit" name="submit" value="commit" class="btn btn-primary" style="display:none;" disabled>
                        commit story to /auto/pending
                    </button>
                </form>
        </div>
    </div>
</div>

<?php include "footer.php"; ?>
</body>
</html>
