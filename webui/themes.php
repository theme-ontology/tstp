<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>TSTP themes</title>

<?php include "header.php"; ?>

    <script>
        var dataUrl = 'json.php?type=theme&fields=name,parents,description,score&slimit=200&rlimit=10000&fuzzysearch=';
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
						[ 1, "asc" ],
						[ 0, "asc" ],
					],
			        "columnDefs" : [
			        	{
						    "render": function ( data, type, row ) {
						    	urldata = encodeURIComponent(data);
						        return "<A href=\"theme.php?name=" + urldata + "\">" + data + "</A>";
						    },
			        		"className": "theme-cell",
						    "targets": 0,
						},
			        	{
						    "render": function ( data, type, row ) {
						    	val = data.split(",")[0];
						        return val;
						    },
						    "targets": 1,
						},
			        	{
			        		"className": "description-cell",
						    "targets": 2,
						},
                        { "targets": 3, "visible": false,},
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
                var url = 'json.php?type=theme&fields=name,parents,description,score&slimit=200&rlimit=10000&fuzzysearch=' + fuzzy;
                console.log(fuzzy);
                table.order([
                    [ 3, "desc" ],
                ]);
                table.column(3).visible(true);
                table.ajax.url(url).load();
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

        <form onkeypress="return event.keyCode != 13;">
            <fieldset class="form-group">
                <label for="fieldFind">Fuzzy Search:</label>
                <input id="fieldFind" type="text" class="form-control" onchange="scheduleReload()" oninput="scheduleReload()">
            </fieldset>
        </form>


        <div id="div_themes_datatable" class="col-md-12">
        	<div class="basebox">
	            <table id="themes_datatable" class="display table table-striped" cellspacing="0" width="100%">
			        <thead>
			            <tr>
			                <th>Theme</th>
			                <th>Parent</th>
                            <th>Description</th>
                            <th>Score</th>
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
