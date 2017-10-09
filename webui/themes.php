<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>TSTP themes</title>

<?php include "header.php"; ?>

    <script>
        // we have moved from server-side fuzzy search to client-side: "fuzzysearch" is vestigial
        var dataUrl = 'json.php?type=theme&fields=score,name,parents,description&slimit=200&rlimit=10000&fuzzysearch=';
        var reloads = 0;
        var dataset = null;
        var tableready = false;
        var fuzzyQuery = "";

        $.ajax({
            "url": dataUrl,
            "success": function(result, status, xhr) {
                dataset = result["data"];
                scheduleReload();
            },
        });

        $(document).ready(function () {
            initDataTable();
        });

        function makeThemeLink(data, color = null)
        {
            urldata = encodeURIComponent(data);
            if (color)
            {
                return '<A style="color:' + color + ';" href="theme.php?name=' + urldata + '">' + data + '</A>';
            }
            return "<A href=\"theme.php?name=" + urldata + "\">" + data + "</A>";
        }

        function initDataTable() {
		    $('#themes_datatable').DataTable( {
		        "pageLength" : 50,
		        "paging" : false,

				"order": [
					[ 2, "asc" ],
					[ 1, "asc" ],
				],

                "language": {
                    "search": "filter:"
                },

		        "columnDefs" : [
                    { 
                        "render": function ( data, type, row ) {
                            return parseFloat(data).toFixed(2);
                        },
                        "targets": 0, 
                        "visible": false,
                    },
		        	{
					    "render": function ( data, type, row ) {
					        return makeThemeLink(data);
					    },
		        		"className": "tstp-theme-cell",
					    "targets": 1,
                        "width": "20%",
					},
		        	{
					    "render": function ( data, type, row ) {
					    	val = data.split(",")[0];
                            return makeThemeLink(val, "black");
					    },
					    "targets": 2,
                        "width": "10%",
					},
		        	{
                        "className": "tstp-description-cell",
					    "targets": 3,
					},
		    	]
		    } );
            tableready = true;
        }

        // compute the edit distance between two strings - less means similar
        function levenshtein(a, b) 
        {
            var matrix = [];
            var i;
            var j;

            if(a.length === 0) return b.length;
            if(b.length === 0) return a.length;
            for (i = 0; i <= b.length; i++) matrix[i] = [i];
            for (j = 0; j <= a.length; j++) matrix[0][j] = j;
            for(i = 1; i <= b.length; i++)
            {
                for(j = 1; j <= a.length; j++)
                {
                    if(b.charAt(i-1) == a.charAt(j-1))
                    {
                        matrix[i][j] = matrix[i-1][j-1];
                    } 
                    else
                    {
                        var insrt = matrix[i][j-1];
                        var delt = matrix[i-1][j];
                        var subst = matrix[i-1][j-1];
                        matrix[i][j] = Math.min(insrt, delt, subst) + 1;
                    }
                }
            }
            return matrix[b.length][a.length];
        }

        // modification of above, find a substring of haystack that has 
        // minimal edit distance with needle and return the distance
        function substrLevenshtein(haystack, needle) 
        {
            var a = haystack;
            var b = needle;
            var matrix = [];
            var i;
            var j;

            if(a.length === 0) return b.length;
            if(b.length === 0) return a.length;
            for (i = 0; i <= b.length; i++) matrix[i] = [i];
            for (j = 0; j <= a.length; j++) matrix[0][j] = 0;
            for(i = 1; i <= b.length; i++)
            {
                for(j = 1; j <= a.length; j++)
                {
                    if(b.charAt(i-1) == a.charAt(j-1))
                    {
                        matrix[i][j] = matrix[i-1][j-1];
                    } 
                    else
                    {
                        var insrt = matrix[i][j-1];
                        var delt = matrix[i-1][j];
                        var subst = matrix[i-1][j-1];
                        matrix[i][j] = Math.min(insrt, delt, subst) + 1;
                    }
                }
            }
            return matrix[b.length].reduce(function(n1, n2) {
                return Math.min(n1, n2);
            });
        }

        // a split function that respects double quotes
        function splitTokens(a)
        {
            return a.match(/\S+|"[^"]+"/g) || [];
        }

        // compare query to theme-name/parents/description record of a theme 
        // return [0, 1] where 0 indicates that all tokens in query were perfectly matched
        function themeCompare(theme, parents, description, query)
        {
            var tokens = splitTokens(query);
            var score = 0.0;

            for (var i = 0; i < tokens.length; i++)
            {
                var s1 = substrLevenshtein(tokens[i], theme) * 1.0 / tokens[0].length;
                var s2 = substrLevenshtein(tokens[i], parents) * 1.0 / tokens[0].length;
                var s3 = substrLevenshtein(tokens[i], description) * 1.0 / tokens[0].length;
                s2 = (s2 + 0.2) / 1.2;
                s3 = (s3 + 0.4) / 1.4;
                score += Math.min(s1, s2, s3);
            }

            return score / tokens.length;
        }

        // do this in blocks in order to keep ui responsive - stop if query changes
        function computeScoresPart(from_idx, presentQuery)
        {
            var end_idx = from_idx + 100;
            //console.log(from_idx + ":: " + presentQuery + " :: " + fuzzyQuery);
            if (fuzzyQuery != presentQuery) return;

            for (var ridx = 0; ridx < dataset.length; ridx++)
            {
                if (ridx > end_idx)
                    return setTimeout(function() { 
                        computeScoresPart(ridx, presentQuery);
                    }, 10);

                var rec = dataset[ridx];
                var score = 1.0 - themeCompare(rec[1], rec[2], rec[2], fuzzyQuery);
                rec[0] = score;
            }

            reloadData();
        }

        // once both data and table are ready, update table with data
        function reloadData()
        {
            console.log("reloadData: " + tableready);
            if (!tableready) return scheduleReload();

            for (var ridx = 0; ridx < dataset.length; ridx++)
            {
                var rec = dataset[ridx];
                var score = 1.0 - themeCompare(rec[1], rec[2], rec[3], fuzzyQuery);
                rec[0] = score;
            }

            var table = $('#themes_datatable').DataTable();
            if (fuzzyQuery)
            {
                table.order([
                    [ 0, "desc" ],
                ]);
                table.column(0).visible(true);
            } else {
                table.order([
                    [ 2, "asc" ],
                    [ 1, "asc" ],
                ]);
                table.column(0).visible(false);
            }
            table.clear().draw();
            table.rows.add(dataset).draw();
        }

        // whenever query changes, schedule a recompute
        function scheduleReload()
        {
            fuzzyQuery = $('#fieldFind').val();
            setTimeout(function() { 
                computeScoresPart(0, fuzzyQuery);
            }, 500);
        }

    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">

        <div style="padding: 1em 4em;">
            <form autocomplete="off" onkeypress="return event.keyCode != 13;">
                <fieldset class="form-group">
                    <label for="fieldFind">Fuzzy Search:</label>
                    <input id="fieldFind" type="text" class="form-control" style="background:#fff2e0;" autofocus 
                        onchange="scheduleReload()" oninput="scheduleReload()">
                </fieldset>
            </form>
        </div>

        <div id="div_stories_datatable" class="col-md-12">
            <div class="basebox">
                <table id="themes_datatable" class="display table table-striped" cellspacing="0" width="100%">
        	        <thead>
        	            <tr>
                            <th>Score</th>
        	                <th>Theme</th>
        	                <th>Parent</th>
                            <th>Description</th>
        	            </tr>
        	        </thead>
        	    </table>
            </div>
        </div>

    </div>
</div>


<?php include "footer.php"; ?>

</body>
</html>
