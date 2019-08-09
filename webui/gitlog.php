<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>TSTP GIT commits</title>

<?php include "header.php"; ?>

    <script>
        var BASE_URL = "json.php?action=commits_log";

        $(document).ready(function () {
            loadDataOnReady();
        });

        function loadDataOnReady() {
            $(document).ready(function() {
			    $('#commits_datatable').DataTable( {
			        "ajax": BASE_URL,
			        "pageLength" : 100,
			        "paging" : true,
                    "lengthMenu": [ 10, 100, 1000, 10000 ],
                    "order": [
                        [ 1, "desc" ],
                    ],
                    "dom": '<"top"flip>rt<"bottom"><"clear">',
                    "language": {
                        "search": "filter:"
                    },
			        "columnDefs" : [
                        {
                            "targets": 0,
                            "className": "tstp-gitid-cell",
                            "width": "20%",
                            "render": function ( data, type, row ) {
                                return '<A href="https://github.com/theme-ontology/theming/commit/' + data + '">' + data + '</A>';
                            },
                        },
                        { 
                            "targets": 1, 
                        },
			        	{
						    "targets": 2,
						},
			        	{
						    "targets": 3,
                            "className": "tstp-description-cell",
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
        <H1 class="px-3">Project History</H1>
    </div>

    <div class="row justify-content-md-center">
        <div id="div_commits_datatable" class="col-md-6">
            <A href="/pub/tstpviz/commit_history.svg"><IMG width="100%" src="/pub/tstpviz/commit_history.svg"></A>
        </div>
        <div id="div_commits_datatable" class="col-md-6">
            <A href="/pub/tstpviz/all_stories_by_year.svg"><IMG width="100%" src="/pub/tstpviz/all_stories_by_year.svg"></A>
        </div>
    </div>

    <div class="row">
        <H3 class="px-3">Git Repository Log</H3>

        <div id="div_commits_datatable" class="col-md-12 hpad0">
        	<div class="basebox">
	            <table id="commits_datatable" class="display table table-striped" cellspacing="0" width="100%">
			        <thead>
			            <tr>
                            <th>ID</th>
                            <th>Time</th>
			                <th>Author</th>
			                <th>Message</th>
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
