<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>Theme Ontology themes</title>

<?php include "header.php"; ?>

    <script>
        var dataUrl = 'json.php?type=theme&fields=score,name,parents,description&slimit=200&rlimit=10000&fuzzysearch=';
        var reloads = 0;
        var prevsearch = "";

        $(document).ready(function () {
            loadDataOnReady();
        });

        // why is this not picked up from tstp_util.js?
        function makeThemeLink(data, color = null)
        {
            urldata = encodeURIComponent(data);
            if (color)
            {
                return '<A style="color:' + color + ';" href="theme.php?name=' + urldata + '">' + data + '</A>';
            }
            return "<A href=\"theme.php?name=" + urldata + "\">" + data + "</A>";
        }

        // multiple themes are separated by newlines (once was commas)
        function makeThemeLinkList(data, color = null)
        {
            html = "";
            parents = data.split("\n");
            for (ii = 0; ii < parents.length; ii++)
            {
                cleanparent = parents[ii].trim();
                if (cleanparent)
                {
                    fmtparent = makeThemeLink(cleanparent, color = color);
                    html += fmtparent + "\n";
                }
            }
            return html;
        }

        function loadDataOnReady() {
            $(document).ready(function() {
			    $('#themes_datatable').DataTable( {
			        "ajax": dataUrl,
                    "pageLength" : 100,
                    "paging" : true,
                    "lengthMenu": [ 10, 100, 1000, 10000 ],

					"order": [
						[ 2, "asc" ],
						[ 1, "asc" ],
					],
                    "dom": '<"top">rt<"bottom"flip><"clear">',
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
                                return makeThemeLinkList(data, "black");
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
			} );
        }

        function reloadData(force=false)
        {
            var fuzzy = $('#fieldFind').val();

            if (!force)
                reloads -= 1;

            if ((reloads == 0 && fuzzy != prevsearch) || force)
            {
                table = $('#themes_datatable').DataTable();
                var url = 'json.php?type=theme&fields=score,name,parents,description&slimit=200&rlimit=10000&fuzzysearch=' + fuzzy;

                if (fuzzy)
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
                table.ajax.url(fuzzy ? url : dataUrl).load();
                prevsearch = fuzzy;
            }
        }

        function scheduleReload()
        {
            reloads += 1;
            setTimeout(reloadData, 500);
        }

        $(document).keyup(function(e) {
            if (e.keyCode == 27) {
                $('#fieldFind').val("");
                reloadData(true);
            }
        });

    </script>

</head>

<body style="overflow-y: scroll;">
<?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">
        <DIV style="float:left;"><IMG src="img/icon-idea.svg" height="80em"></DIV>
        <div style="padding: 0.7em 1em 0em 6.5em;">
            <form autocomplete="off" onkeypress="return event.keyCode != 13;">
                <fieldset class="form-group">
                    <label for="fieldFind">Theme Search:</label>
                    <input id="fieldFind" type="text" class="form-control search-theme" autofocus 
                        onchange="scheduleReload()" oninput="scheduleReload()">
                </fieldset>
            </form>
        </div>

        <div id="div_stories_datatable" class="col-md-12 hpad0">
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
