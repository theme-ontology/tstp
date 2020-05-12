<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Theme Ontology M-4 Git Search Tool</title>
<?php include "header.php"; ?>

<script>
    var BASE_URL = "m4notify";

    function doSearch() {
        var query = $('#fieldFind').val();
        var data = {
            name: "gitsearch",
            query: encodeURIComponent(query),
        };
        if (query.length > 2) {
            table = $('#response_datatable').DataTable();
            table.clear().draw();
            $.getJSON(BASE_URL, data, receiveSearchResponse);
            $('#fieldSubmit').prop('disabled', true);
            $('#fieldSubmit').prop('value', "working...");
        } else {
            $('#fieldSubmit').prop('value', "Execute Function (need 3+ characters)");
        }
        return false;
    }

    function receiveSearchResponse(data) {
        $('#fieldSubmit').prop('disabled', false);
        $('#fieldSubmit').prop('value', "Execute Function");
        rows = data["data"];
        table = $('#response_datatable').DataTable();
        table.rows.add(rows);
        table.draw();
    }

    $(document).ready(function() {
        $('#response_datatable').DataTable( {
            "paging" : false,
            "searching": false,
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
                    "width": "15%",
                    "render": function ( data, type, row ) {
                        return '<A href="https://github.com/theme-ontology/theming/commit/' + data + '">' + data + '</A>';
                    },
                },
                { 
                    "width": "10%",
                    "targets": 1, 
                },
                {
                    "width": "5%",
                    "targets": 2,
                },
                {
                    "width": "10%",
                    "targets": 3,
                    "className": "tstp-description-cell",
                    "render": function ( data, type, row ) {
                        var url = "https://github.com/theme-ontology/theming/blob/" + row[0] + "/" + data;
                        return '<A href="' + url + '">' + data + '</A>';
                    },
                },
                {
                    "targets": 4,
                    "width": "60%",
                    "className": "tstp-code-cell",
                    "render": function ( data, type, row ) {
                        if (data.startsWith("-"))
                            return '<span style="color:#aa0000;">' + data + '</span>';
                        else if (data.startsWith("+"))
                            return '<span style="color:#008800;">' + data + '</span>';
                        else
                            return data
                    },
                },
            ]
        } );
    } );

</script>
</head>

<body style="overflow-y: scroll;"><?php include "navbar.php"; ?>

<div class="container main-body">
    <div class="row">
        <div class="basebox">
            <P><IMG src="img/icon-machine.svg" height="100px"></P>
            <H4>M-4 Robotic Extension</H4>
        </div>
        <div class="basebox">
            <form autocomplete="off" onsubmit="return doSearch()" action="noop">
                <fieldset class="form-group">
                    <label for="fieldFind">Git History Search (regex):</label>
                    <input id="fieldFind" type="text" class="form-control search-story" autofocus>
                    <input id="fieldSubmit" type="submit" value="Execute Function">
                </fieldset>
            </form>
        </div>

        <div id="div_datatable" class="col-md-12 hpad0">
            <div class="basebox">
                <table id="response_datatable" class="display table table-striped" cellspacing="0" width="100%">
                    <thead>
                        <tr>
                            <th>Commit</th>
                            <th>Time</th>
                            <th>Author</th>
                            <th>File</th>
                            <th>Line</th>
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
