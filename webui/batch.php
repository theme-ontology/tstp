<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>TSTP</title>
<?php include "header.php"; ?>

    <script>
    	var eventsTable;
    	var displayMessages = [];

    	function displayMessage(idx)
    	{
    		alert(displayMessages[idx]);
    	}

    	function hoverMessage(idx)
    	{
    		$("#tableTooltip").attr("visible", true);
    		$("#tableTooltip").style("opacity", 1);
    	}
    	function hoverOff()
    	{
    		$("#tableTooltip").attr("visible", false);
    		$("#tableTooltip").style("opacity", 0);
    	}

        $(document).ready(function () {
            loadTablesOnReady();
        });

        function tstpObjFormat(objType, data)
    	{
	    	if (objType == "theme")
	    	{
		    	urldata = encodeURIComponent(data);
		        return "<A href=\"theme.php?name=" + urldata + "\">" + data + "</A>";
		    }
	    	else if (objType == "story")
	    	{
		    	urldata = encodeURIComponent(data);
                return "<A href=\"story.php?name=" + urldata + "\">" + data + "</A>";
		    }
		    return data;
    	}

        function loadTablesOnReady() {
            $(document).ready(function() {
			    eventsTable = $('#events_datatable').DataTable( {
			        "ajax": 'json.php?type=proposedevents&fields=entrytime,action,category1,name1,category2,name2,field,newvalue,oldvalue&slimit=2000&rlimit=100',
			        "pageLength" : 10,
			        "paging" : true,
					"order": [
						[ 0, "desc" ],
					],

			        "columnDefs" : [
						{
							"targets": 0,
							"visible": false,
						},
						{
							"targets": 1,
						    "render": function ( data, type, row ) {
						    	idx = displayMessages.length;
						    	message = ""
						    	message += "OLD VALUE:\n" + row[8] + "\n\n";
						    	message += "NEW VALUE:\n" + row[7] + "\n\n";
						    	displayMessages.push(message);

						    	if (row[1] != "insert")
						    	{
						    		return "<A href='#' class='locallink' onClick='displayMessage(" + idx + ")' >" + data + "</A>";
						    	}
						    	else
						    	{
						    		return data;
						    	}
						    },
						},
						{ "targets": 2, "visible": false,},
						{ "targets": 4, "visible": false,},
			        	{
						    "render": function ( data, type, row ) {
						    	return tstpObjFormat(row[2], data);
						    },
						    "targets": 3,
						},
			        	{
						    "render": function ( data, type, row ) {
						    	return tstpObjFormat(row[4], data);
						    },
						    "targets": 5,
						},
			        	{
						    "targets": 6,
						},
						{ "targets": 7, "visible": true, "className": "lightcell"},
						{ "targets": 8, "visible": false,},
			    	],

			        "createdRow": function ( row, data, index ) {
			            if ( data[1] == 'reverted' ) 
			            {
			                $('td', row).addClass('row_revert');
			            }
			            else if ( data[1] == 'pending' ) 
			            {
			                $('td', row).addClass('row_pending');
			            }
			        },

			    } );

			    $('#events_datatable td').on('click', 'td', function () {
			        var data = table.row(this).data();
			        alert();
			    } );

			} );
        }

		function updateButtonStatus()
		{
	        var val = $('#fieldVerify').is(':checked');
	        $('#commitbutton').attr("disabled", !val);
		}

    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container">
<?php
	$submit = $_POST["submit"];
	$response = "";
	$result = "";

	// file upload condition: step in file upload process taken
	if($submit) {
		// python handles all of this
		require_once("pythonlib.php");
		$response = tstp_run_python('python ../pylib/webupload.py');
		echo $response;

		if (substr($response, 0, 7) === "Nothing") {
			$result = "nothing";
			$submit = "";
		} elseif ($response) {
			$result = "something";
		}
	}
?>

<?php
	// result of current operation if any
	if ($result == "something") {
?>
    <div class="row">
        <div class="alert alert-info">
        	<?php echo $response; ?>
        </div>
    </div>
<?php
	} 
?>
<?php
	if ($result == "nothing") {
?>
    <div class="row">
        <div class="alert alert-danger">
        	<?php echo $response; ?>
        </div>
    </div>
<?php
	} 
?>


<?php
	// status of previous operation
	if ($submit == "commit") {
?>
    <div class="row">
        <div class="alert alert-success">
        	Changes were committed.
        </div>
    </div>
<?php
	} elseif ($submit == "cancel") {
?>
    <div class="row">
        <div class="alert alert-danger">
        	Operation cancelled.
        </div>
    </div>
<?php
	} 
?>


<?php
	// show form unless file was just submitted
	if ($submit != "submitfile") {
?>
    <div class="row">
        <div class="col-md-6">
            <div class="basebox">
            	Upload a spreadsheet with new data. 
            	The proposed changes will be displayed for verification before they are committed.
            	Check <A href="resources.php">resources</A> for templates to use.
            </div>
        </div>
        <div class="col-md-6">
            <div class="alert alert-info">
           		<form method="post" enctype="multipart/form-data">
        			<fieldset class="form-group">
        				<label for="fieldType">What?</label>
    					<select id="fieldType" name="fieldType" type="file">
    						<option value="storythemes">Story Themes</option>
    						<option value="themedefinitions">Theme Definitions</option>
    						<option value="storydefinitions">Story Definitions</option>
    					</select>
        			</fieldset>
        			<fieldset class="form-group">
        				<label for="fieldFile">Choose the data file (spreadsheet) to upload:</label>
    					<input id="fieldFile" name="fieldFile" type="file">
        			</fieldset>
    				<button type="submit" name="submit" value="submitfile" class="btn btn-primary btn-block">Verify Data</button>
        		</form>
            </div>
        </div>

    </div>
<?php
	}
?>

<?php
	// file upload condition: file was just uploaded, show prospective changes and options
	if ($submit == "submitfile") {
?>
    <div class="row">
		<H2>Proposed Actions</H2>

        <div id="div_datatable" class="col-md-12">
        	<div class="basebox">
	            <table id="events_datatable" class="display table table-striped" cellspacing="0" width="100%">
			        <thead>
			            <tr>
			                <th>Time</th>
			                <th>Type</th>
			                <th>What1</th>
			                <th>Object1</th>
			                <th>What2</th>
			                <th>Object2</th>
			                <th>Attribute</th>
			                <th>NewValue</th>
			                <th>OldValue</th>
			            </tr>
			        </thead>
			    </table>
			</div>
		</div>
    </div>

    <div class="row">
        <div class="col-md-6">
            <div class="alert alert-info">
           		<form method="post" enctype="multipart/form-data">
        			<fieldset class="form-group">
    					<input id="fieldVerify" type="checkbox" OnChange="updateButtonStatus()">
        				<label for="fieldVerify">Are the changes all in order?</label>
        			</fieldset>
    				<button id="commitbutton" type="submit" name="submit" value="commit" class="btn btn-primary" disabled>Commit Changes</button>
    				<button type="submit" name="submit" value="cancel" class="btn btn-danger">Cancel</button>
        		</form>
            </div>
        </div>
    </div>
<?php
	} 
?>



</div>


<?php include "footer.php"; ?>

</body>
</html>
