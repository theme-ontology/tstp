<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<?php 
	$SID = $_GET['name'];
?>
<head>
	<meta charset="UTF-8">
	<title>TSTP <?php echo $SID; ?></title>

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
            $(document).ready(function() {
			    var table = $('#themes_datatable').DataTable( {
			        "ajax": 'json.php?type=storytheme&fields=name2,weight,motivation&f1=' + g_objName + '&slimit=200&rlimit=10000',
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
						    "targets": 1,
						},
			        	{
			        		"width": "60%",
			        		"className": "description-cell",
						    "targets": 2,
						},
			    	],
			    } );
			} );

        }
    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">
        <div class="col-md-12">
            <H3>Story</H3>
        </div>
    </div>

<?php // Basic information //?>
    <div class="row">
        <div id="div_maininfo" class="basebox">

            <div class="col-md-12">
                <div class="panel panel-default">
                    <div class="panel-heading"><?php echo $SID; ?></div>
                    <div class="panel-body">
                        <dl>
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

<?php // THEMES TABLE //?>
    <div class="row">
        <div id="div_datatable" class="col-md-12">
        	<div class="basebox">
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
