<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<?php 
	$SID = $_GET['name'];
?>
<head>
	<meta charset="UTF-8">
	<title>Theme Ontology <?php echo $SID; ?></title>

<?php include "header.php"; ?>

    <script>
        var g_objType = "story";
        var g_objName = "<?php echo $SID; ?>";
        var g_objFields = [ "name", "title", "date", "description" ];

        var g_objDefs = {
        	"main" : {
        		"type" : "story",
        		"name" : "<?php echo $SID; ?>",
        		"fields" : [ "name", "title", "date", "description" ],
        	},
        	"theme" : {
        		"type" : "story",
        		"name" : "<?php echo $SID; ?>",
        		"fields" : [ "name", "title", "date", "description" ],
        	},

        };

    </script>

    <script type="text/javascript" src="js/tstp_objinfo.js"></script>

    <script>
        $(document).ready(function () {
            loadTablesOnReady();
            loadTypeaheadOnReady();
        });


        function loadTypeaheadOnReady() {
			var bh = new Bloodhound({
				datumTokenizer: Bloodhound.tokenizers.whitespace,
				queryTokenizer: Bloodhound.tokenizers.whitespace,
				prefetch: 'json.php?action=themelist'
			});

            $('#fieldTheme').typeahead(
            	null,
            {
				name: 'states',
				limit: 20,
				source: bh,
            });
        }


        function loadTablesOnReady() {
            var BASE_URL = "json.php?type=story&fields=score,name,title,date,description&slimit=200&rlimit=10000";
            var sidurldata = encodeURIComponent(g_objName);
            var sidurl = BASE_URL + "&collectionfilter=" + sidurldata;

            $(document).ready(function() {
			    var table = $('#themes_datatable').DataTable( {
			        "ajax": 'json.php?type=storytheme&fields=name2,weight,motivation&f1=' + g_objName + '&slimit=200&rlimit=10000',
			        "pageLength" : 50,
			        "paging" : false,
                    "searching": false,
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
						    "targets": 1,
						},
			        	{
			        		"width": "60%",
			        		"className": "description-cell",
						    "targets": 2,
						},
			    	],
                    "initComplete": function(settings, json) {
                        $('#loading_message').css('display','none');
                    }
			    } );

                if (g_objName.startsWith("collection:") || g_objName.startsWith("Collection:"))
                {
                    $('#member_stories').css('display','inline');

                    var table2 = $('#stories_datatable').DataTable( {
                        "ajax": sidurl,
                        "paging" : false,
                        "searching": false,
                        "order": [
                            [ 3, "desc" ],
                            [ 2, "asc" ],
                        ],
                        "columnDefs" : [
                            {
                                "visible": false,
                                "targets": 0,
                            },
                            {
                                "render": function ( data, type, row ) {
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
                        ],
                        "initComplete": function(settings, json) {
                            $('#stories_loading_message').css('display','none');
                        }
                    } );
                }
			} );

        }
    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">
<?php // Basic information //?>
    <div class="row">
        <div id="div_maininfo" class="basebox">

            <div class="col-md-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <div style="float:right;"><H4><span class="label label-story">story</span></H4></div>
                        <H4><?php echo $SID; ?></H4>
                    </div>
                    <div class="panel-body">
                        <dl class="dl-horizontal text-left">
                            <dt>Title:</dt> <dd><span id="obj_title"></span></dd>
                            <dt>Date:</dt> <dd><span id="obj_date"></span></dd>
                        </dl>
                        <P>
                            <div id="div_description"></div>
                        </P>
                    </div>
                </div>
            </div>
        </div>
    </div>


<?php // COLLECTION MEMBER STORIES //?>
    <div id="member_stories" style="display:none">
        <div class="row">
            <div id="div_stories_datatable" class="col-md-12 hpad0">
                <div class="basebox">
                    <H4>List of Member Stories</H4>
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

        <div id="stories_loading_message" class="row">
            <div class="basebox">loading...</div>
        </div>
    </div>


<?php // THEMES TABLE //?>
    <div class="row">
        <div id="div_datatable" class="col-md-12 hpad0">
        	<div class="basebox">
                <H4>List of Themes</H4>
	            <table id="themes_datatable" class="display table table-striped" cellspacing="0" width="100%">
			        <thead>
			            <tr>
			                <th>Theme</th>
			                <th>Weight</th>
			                <th>Motivation</th>
			            </tr>
			        </thead>
			    </table>
			</div>
		</div>
    </div>

    <div id="loading_message" class="row">
        <div class="basebox">loading...</div>
    </div>

</div>

<?php include "footer.php"; ?>

</body>
</html>
