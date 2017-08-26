<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<?php
	$THEME = $_GET['name'];
    $THME_URL = urlencode($THEME);
?>
<head>
	<meta charset="UTF-8">
	<title>TSTP <?php echo $THEME; ?></title>

<?php include "header.php"; ?>

    <script>
        var g_objType = "theme";
        var g_objName = "<?php echo $THEME; ?>";
        var g_objFields = [ "name", "title", "description" ];
        var g_objInfoBoxes = [ "parents", "children" ];
    	var g_objData;
    </script>
    <script type="text/javascript" src="js/tstp_webform.js"></script>
    <script type="text/javascript" src="js/tstp_objinfo.js"></script>

    <script>
        $(document).ready(function () {
            loadTablesOnReady();
        });

        function loadTablesOnReady() {
            $(document).ready(function() {
                $('#stories_datatable').DataTable( {
                    "ajax": 'json.php?type=storytheme&fields=name1,weight,motivation&f2=' + encodeURIComponent(g_objName) + '&slimit=200&rlimit=10000',
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
                                return "<A href=\"story.php?name=" + urldata + "\">" + data + "</A>";
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
                    ]
                } );
            } );
        }
    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">
    <div id="loading_message" class="row">
    	<div class="basebox">loading...</div>
    </div>


<?php // MAIN FORM //?>
    <div id="hidden_form" class="row" style="visibility:hidden;">

        <div id="div_obj_basics1" class="col-md-8 col-sm-12">
        	<div class="basebox">
        		<form>
        			<fieldset class="form-group">
        				<label for="fieldName">Theme</label>
        				<input id="fieldName" type="text" class="form-control">
        			</fieldset>

        			<fieldset class="form-group">
        				<label for="fieldDescription">Description</label>
        				<textarea id="fieldDescription" rows=10 class="form-control"></textarea>
        			</fieldset>
        		</form>
			</div>
		</div>

        <div id="div_obj_submit" class="col-md-4 col-sm-12">
        	<div class="sidebox">
    			<fieldset class="form-group">
    				<button onClick="submitData()" class="btn btn-primary btn-block">Submit Changes</button>
    			</fieldset>

<?php // Theme INFO //?>
                <div id="div_infobox" style="display:none; padding: 0px 0px; margin: 0px 0px;">
                    <div id="div_parents"></div>
                    <div id="div_children"></div>
                </div>

	        </div>
        </div>
    </div>


<?php // Stories TABLE //?>
    <div class="row">

        <div id="div_datatable" class="col-md-12">
            <div class="basebox">
                <table id="stories_datatable" class="display table table-striped" cellspacing="0" width="100%">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Weight</th>
                            <th>Motivation</th>
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
