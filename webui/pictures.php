<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>TSTP</title>
<?php include "header.php"; ?>

<script>
    // replace href=":xxxx/relative/path" type specs
    function fixRelativePort(target)
    {
        if (target.tagName.toLowerCase() == 'a')
        {
            var port = target.getAttribute('href').match(/^:(\d+)(.*)/);
            if (port)
            {
                if (target.port == "8080")
                {
                    target.href = port[2];
                    target.port = String(parseInt(port[1]) + 1);
                } 
                else
                {
                    target.href = port[2];
                    target.port = port[1];		      
                }
            }
        }        
    }

	// delegate event for performance, and save attaching a million events to each anchor
	document.addEventListener('click', function(event) {
        fixRelativePort(event.target);
	}, false);

</script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container">
    <div class="row">

        <div class="col-sm-12 col-md-8 col-lg-6">
			<div class="panel panel-default">
				<div class="panel-body">
	              	<H3 class="px-3">Data Exploration and Visualization</H3>
	            	<TABLE class="table table-striped">
		            	<tbody>
                            <tr>
                                <td><A href = ":3838/shiny/">Story Simularity</A></td>
                                <td>Pick a story and see other stories that are thematically similar.</td>
                            </tr>
                            <tr>
                                <td><A href = "svg.php?subject=themecube">Star Trek tos/tas/tng Theme Domain Distribution</A></td>
                                <td>
                                    A case study of how themes are distributed between the three early Star Trek TV Series. 
                                    This delineates, to an extent, how the show changed over the years.
                                </td>
                            </tr>
                        </tbody>
	            	</TABLE>
            	</div>
            </div>
        </div>


    </div>
</div>


<?php include "footer.php"; ?>

</body>
</html>
