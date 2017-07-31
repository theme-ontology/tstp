<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>TSTP stories</title>

<?php include "header.php"; ?>

    <script>
        $(document).ready(function () {
            loadDataOnReady();
        });

        function loadDataOnReady() {
            $(document).ready(function() {
			    $('#stories_datatable').DataTable( {
			        "ajax": 'json.php?type=story&fields=name,title,date,description&slimit=200&rlimit=10000',
			        "pageLength" : 50,
			        "paging" : false,
                    "order": [],

			        "columnDefs" : [
			        	{
						    "render": function ( data, type, row ) {
						    	urldata = encodeURIComponent(data);
						        return "<A href=\"story.php?name=" + urldata + "\">" + data + "</A>";
						    },
			        		"className": "tstp-sid-cell",
						    "targets": 0,
						},
			        	{
			        		"width": "30%",
						    "targets": 1,
						},
			        	{
			        		"className": "tstp-date-cell",
						    "targets": 2,
						},
			        	{
			        		"className": "tstp-description-cell",
						    "targets": 3,
						},
			    	]
			    } );
			} );
        }
    </script>

</head>

<body><?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">

        <div id="div_stories_datatable" class="col-md-12">
        	<div class="basebox">
	            <table id="stories_datatable" class="display table table-striped" cellspacing="0" width="100%">
			        <thead>
			            <tr>
			                <th>ID</th>
			                <th>Title</th>
			                <th>Date</th>
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
