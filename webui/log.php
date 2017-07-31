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
			        "ajax": 'json.php?type=event&fields=entrytime,action,category1,name1,category2,name2,field,newvalue&slimit=2000&rlimit=100',
			        "pageLength" : 10,
			        "paging" : true,
					"order": [
						[ 0, "desc" ],
					],

			        "columnDefs" : [
						{
                            "className": "tstp-date-cell",
							"targets": 0,
							"width": "15%",
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
						    "render": function ( data, type, row ) {
						    	idx = displayMessages.length;
						    	displayMessages.push("NEW VALUE:\n\n" + row[7]);
						    	return "<A href='#' onClick='displayMessage(" + idx + ")' >" + data + "</A>";
						    },
						    "targets": 6,
						},
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
    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container">
    <div class="row">

<?php // EVENTS TABLE //?>
    <div class="row">
		<H2>Recent Events</H2>

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
			            </tr>
			        </thead>
			    </table>
			</div>
		</div>


    </div>

    </div>
</div>


<?php include "footer.php"; ?>

</body>
</html>
