<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>TSTP</title>
<?php include "header.php"; ?>

<script>
	// delegate event for performance, and save attaching a million events to each anchor
	document.addEventListener('click', function(event) {
	  var target = event.target;
	  if (target.tagName.toLowerCase() == 'a')
	  {
	      var port = target.getAttribute('href').match(/^:(\d+)(.*)/);
	      if (port)
	      {
	         target.href = port[2];
	         target.port = port[1];
	      }
	  }
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
	            	</TABLE>
            	</div>
            </div>
        </div>


    </div>
</div>


<?php include "footer.php"; ?>

</body>
</html>
