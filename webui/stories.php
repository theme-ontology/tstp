<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>TSTP stories</title>

<?php include "header.php"; ?>

    <script>
        var BASE_URL = "json.php?type=story&fields=score,name,title,date,description&slimit=200&rlimit=10000";
        var START_URL = BASE_URL + '&collapsecollections=on';
        var IN_COLLECTION = false;
        var reloads = 0;
        var prevsearch = "";

        $(document).ready(function () {
            loadDataOnReady();
        });

        function loadDataOnReady() {
            $(document).ready(function() {
			    $('#stories_datatable').DataTable( {
			        "ajax": START_URL,
			        "pageLength" : 100,
			        "paging" : true,
                    "lengthMenu": [ 10, 100, 1000, 10000 ],
                    "order": [],

                    "order": [
                        [ 3, "desc" ],
                        [ 2, "asc" ],
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
                                if (!IN_COLLECTION) {
                                    if (data.startsWith("collection:") || data.startsWith("Collection:")) {
                                        var csid = data;
                                        return "<A style='cursor:pointer;' onclick='loadCollectionData(\"" + csid + "\")'>" + data + "</A>";
                                    }
                                }

					            var urldata = encodeURIComponent(data);
					            return "<A href=\"story.php?name=" + urldata + "\">" + data + "</A>";
						    },
			        		"className": "tstp-sid-cell",
						    "targets": 1,
						},
			        	{
			        		"width": "30%",
						    "targets": 2,
						},
			        	{
			        		"className": "tstp-date-cell",
						    "targets": 3,
						},
			        	{
			        		"className": "tstp-description-cell",
						    "targets": 4,
						},
			    	]
			    } );
			} );
        }

        function clearSearchNoReload() {
            IN_COLLECTION = false;
            prevsearch = "";
            $('#fieldFind').val("");
        }

        function loadCollectionData(sid) {
            var table = $('#stories_datatable').DataTable();
            var urldata = encodeURIComponent(sid);
            var url = BASE_URL + "&collectionfilter=" + urldata;
            clearSearchNoReload();
            table.clear().draw();
            table.ajax.url(url).load();
            IN_COLLECTION = true;
        }

        function reloadData(force=false)
        {
            var fuzzy = $('#fieldFind').val();

            if (!force)
                reloads -= 1;

            if ((reloads == 0 && fuzzy != prevsearch) || force)
            {
                table = $('#stories_datatable').DataTable();
                var url = BASE_URL + '&fuzzysearch=' + fuzzy;

                if (fuzzy)
                {
                    table.order([
                        [ 0, "desc" ],
                    ]);
                    table.column(0).visible(true);
                } else {
                    table.order([
                        [ 3, "desc" ],
                        [ 2, "asc" ],
                    ]);
                    table.column(0).visible(false);
                }
                table.clear().draw();
                table.ajax.url(fuzzy ? url : START_URL).load();
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
                clearSearchNoReload();
                reloadData(true);
            }
        });

    </script>

</head>

<body><?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">
        <div style="padding: 0em 4em;">
            <form autocomplete="off" onkeypress="return event.keyCode != 13;">
                <fieldset class="form-group">
                    <label for="fieldFind">Fuzzy Search:</label>
                    <input id="fieldFind" type="text" class="form-control search-story"  autofocus 
                        onchange="scheduleReload()" oninput="scheduleReload()">
                </fieldset>
            </form>
        </div>

        <div id="div_stories_datatable" class="col-md-12 hpad0">
        	<div class="basebox">
                fjdhsabkjh
	            <table id="stories_datatable" class="display table table-striped" cellspacing="0" width="100%">
			        <thead>
			            <tr>
                            <th>Score</th>
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
