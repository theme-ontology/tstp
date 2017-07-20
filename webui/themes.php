<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>TSTP themes</title>

<?php include "header.php"; ?>

    <script>
        var dataUrl = 'json.php?type=theme&fields=score,name,parents,description&slimit=200&rlimit=10000&fuzzysearch=';
        var reloads = 0;

        $(document).ready(function () {
            loadDataOnReady();
        });

        function loadDataOnReady() {
            $(document).ready(function() {
			    $('#themes_datatable').DataTable( {
			        "ajax": dataUrl,
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
						    	urldata = encodeURIComponent(data);
						        return "<A href=\"theme.php?name=" + urldata + "\">" + data + "</A>";
						    },
			        		"className": "theme-cell",
						    "targets": 1,
                            "width": "20%",
						},
			        	{
						    "render": function ( data, type, row ) {
						    	val = data.split(",")[0];
						        return val;
						    },
						    "targets": 2,
                            "width": "10%",
						},
			        	{
			        		"className": "description-cell",
						    "targets": 3,
						},
			    	]
			    } );
			} );
        }

        function reloadData()
        {
            reloads -= 1;

            if (reloads == 0)
            {
                table = $('#themes_datatable').DataTable();
                var fuzzy = $('#fieldFind').val();
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
            }
        }

        function scheduleReload()
        {
            reloads += 1;
            setTimeout(reloadData, 500);
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
