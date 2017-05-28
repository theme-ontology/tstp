<? require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<? 
	$SID = $_GET['name'];
?>
<head>
	<meta charset="UTF-8">
	<title>TSTP <? echo $SID; ?></title>

<? include "header.php"; ?>

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
    <script type="text/javascript" src="js/tstp_webform.js"></script>

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
<? include "navbar.php"; ?>

<div class="container main-body">
    <div id="loading_message" class="row">
    	<div class="basebox">loading...</div>
    </div>


<?php // MAIN FORM //?>
    <div id="hidden_form" class="row" style="visibility:hidden;">

        <div id="div_story_basics" class="col-md-8 col-sm-12">
        	<div class="basebox">
        		<form>
        			<fieldset class="form-group">
        				<label for="fieldTitle">Title</label>
        				<input id="fieldTitle" type="text" class="form-control">
        			</fieldset>

        			<fieldset class="form-group">
        				<label for="fieldDescription">Description</label>
        				<textarea id="fieldDescription" rows=10 class="form-control"></textarea>
        			</fieldset>
        		</form>
			</div>
		</div>

        <div id="div_story_basics2" class="col-md-4 col-sm-12">
        	<div class="sidebox">
        		<form>
        			<fieldset class="form-group">
        				<label for="fieldName">ID</label>
        				<input id="fieldName" type="text" class="form-control">
        			</fieldset>
        		</form>
        		<form>
        			<fieldset class="form-group">
        				<label for="fieldDate">Date</label>
        				<input id="fieldDate" type="text" class="form-control">
        			</fieldset>
        		</form>
	        </div>
        </div>

        <div id="div_story_submit" class="col-md-4 col-sm-12">
            <div class="basebox">
    			<fieldset class="form-group">
    				<button onClick="submitData()" class="btn btn-primary btn-block">Submit Changes</button>
    			</fieldset>
	        </div>
        </div>
    </div>

    <div class="row">
        <div class="basebox">
			<div class="form-group col-sm-12">
	    		<h4>Add/Change Theme</h4>
	    	</div>

			<div class="form-group col-md-3 col-sm-12">
				<select class="form-control" id="sel1">
					<option>minor</option>
					<option>major</option>
					<option>choice</option>
					<option>absent</option>
				</select>
			</div>

			<div class="form-group col-md-9 col-sm-12">
                <fieldset class="form-group">
                    <input id="fieldTheme" class="form-control typeahead" type="text" placeholder="enter a theme">
                </fieldset>
            </div>

			<div class="form-group col-sm-8">
    			<fieldset class="form-group">
    				<label for="fieldMotivate">Motivate this entry</label>
    				<textarea id="fieldMotivate" rows=2 class="form-control"></textarea>
    			</fieldset>
            </div>

	        <div id="div_storytheme_submit" class="col-sm-4">
    			<fieldset class="form-group">
    				<button onClick="submitData()" class="btn btn-primary btn-block">Submit Changes</button>
    			</fieldset>
	        </div>

        </div>
    </div>


<?php // THEMES TABLE //?>
    <div class="row">
		<div class="form-group col-sm-12">
    		<h4>&nbsp;</h4>
    	</div>

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


</div>

<? include "footer.php"; ?>

</body>
</html>
