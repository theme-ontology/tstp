<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>

<head>
	<meta charset="UTF-8">
	<title>Theme Ontology stories</title>

<?php include "header.php"; ?>

    <script>
        var BASE_URL = "json.php?type=story&fields=score,name,title,date,description&slimit=200&rlimit=10000";
        var START_URL = BASE_URL + '&collapsecollections=on';
        var IN_COLLECTION = false;
        var reloads = 0;
        var prevsearch = "";

        $(document).ready(function () {
            var collectionfilter = getQueryVariable("collectionfilter");
            START_URL = getURL(collectionfilter);
            loadDataOnReady();
        });

        window.onpopstate = function(event) {
            var state = event.state;
            clearSearchNoReload();
            if (state && "collectionfilter" in state) {
                loadCollectionData(state["collectionfilter"], false);
            } else {
                START_URL = getURL(false);
                clearSearchNoReload();
                reloadData(true);
            }
        };

        function loadDataOnReady() {
            $(document).ready(function() {
			    $('#stories_datatable').DataTable( {
			        "ajax": START_URL,
			        "pageLength" : 100,
			        "paging" : true,
                    "lengthMenu": [ 10, 100, 1000, 10000 ],
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
                                        // because datatables is even more retarded than javascript
                                        var csid = data.toString().replace("\'", '&&&datatables-is-retarded-quote&&&');
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

        function urlify(val) {
            val = val.replace("&&&datatables-is-retarded-quote&&&", "'");
            var urldata = encodeURIComponent(val);
            return urldata;
        }

        function getURL(collectionfilter=false)
        {
            var url = BASE_URL + '&collapsecollections=on';
            if (collectionfilter) {
                var urldata = urlify(collectionfilter);
                url = BASE_URL + "&collectionfilter=" + urldata;
            }
            return url;
        }

        function loadCollectionData(sid, addhistory=true) {
            var table = $('#stories_datatable').DataTable();
            var url = getURL(sid);
            clearSearchNoReload();
            table.clear().draw();
            table.ajax.url(url).load();
            IN_COLLECTION = true;
            if (addhistory) {
                var urldata = urlify(sid);
                history.pushState(
                    {collectionfilter: sid},
                    "title 1",
                    "?collectionfilter=" + urldata
                );
            }
        }

        function reloadData(force=false)
        {
            var fuzzy = $('#fieldFind').val();
            if (fuzzy.length < 3) fuzzy = "";

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

<body style="overflow-y: scroll;"><?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">
        <DIV style="float:left;"><IMG src="img/icon-book.svg" height="80em"></DIV>
        <div style="padding: 0.7em 1em 0em 6.5em;">
            <form autocomplete="off" onkeypress="return event.keyCode != 13;">
                <fieldset class="form-group">
                    <label for="fieldFind">Story Search:</label>
                    <input id="fieldFind" type="text" class="form-control search-story"  autofocus 
                        onchange="scheduleReload()" oninput="scheduleReload()">
                </fieldset>
            </form>
        </div>

        <div id="div_stories_datatable" class="col-md-12 hpad0">
        	<div class="basebox">
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
