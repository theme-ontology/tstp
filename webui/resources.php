<? require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>TSTP</title>
<? include "header.php"; ?>
</head>

<body>
<? include "navbar.php"; ?>

<div class="container">
    <div class="row">

        <div class="col-sm-12 col-md-8 col-lg-6">
			<div class="panel panel-default">
				<div class="panel-body">
	              	<H3 class="px-3">Batch Data Templates</H3>
	            	<TABLE class="table table-striped">
		            	<tbody>
			            	<tr>
				            	<td><A href = "data/test-storydefinitions-batch.xls">test-storydefinitions-batch.xls</A></td>
				            	<td>Define stories</td>
				            </tr>
			            	<tr>
				            	<td><A href = "data/test-themedefinitions-batch.xls">test-themedefinitions-batch.xls</A></td>
				            	<td>Define themes</td>
				            </tr>
				            <tr>
			            		<td><A href = "data/test-storythemes-batch.xls">test-storythemes-batch.xls</A></td>
			            		<td>Assign themes to stories</td>
			            	</tr>
			            	</tbody>
	            	</TABLE>
            	</div>
            </div>
        </div>


    </div>
</div>


<? include "footer.php"; ?>

</body>
</html>
