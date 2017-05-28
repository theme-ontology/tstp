<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>TSTP themes</title>

<?php include "header.php"; ?>

    <script>
        $(document).ready(function () {
            loadDataOnReady();
        });

        function loadDataOnReady() {
            $(document).ready(function() {
			    $('#themes_datatable').DataTable( {
			        "ajax": 'json.php?type=theme&fields=name,parents,description&slimit=200&rlimit=10000',
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
			    	]
			    } );
			} );
        }
    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">

        <div id="div_themes_datatable" class="col-md-12">
        	<div class="basebox">
	            <table id="themes_datatable" class="display table table-striped" cellspacing="0" width="100%">
			        <thead>
			            <tr>
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
