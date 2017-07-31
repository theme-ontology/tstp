<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>TSTP</title>
<?php include "header.php"; ?>
</head>

<body>
<?php include "navbar.php"; ?>

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
				            	<td>Template to define stories.</td>
				            </tr>
			            	<tr>
				            	<td><A href = "data/test-themedefinitions-batch.xls">test-themedefinitions-batch.xls</A></td>
				            	<td>Template to define themes.</td>
				            </tr>
				            <tr>
			            		<td><A href = "data/test-storythemes-batch.xls">test-storythemes-batch.xls</A></td>
			            		<td>Template to assign themes to stories.</td>
			            	</tr>
			            	</tbody>
	            	</TABLE>
            	</div>
            </div>
        </div>


        <div class="col-sm-12 col-md-8 col-lg-6">
			<div class="panel panel-default">
				<div class="panel-body">
	              	<H3 class="px-3">Download Data</H3>
	            	<TABLE class="table table-striped">
		            	<tbody>
			            	<tr>
				            	<td><A href = "download.php?what=storydefinitions&fmt=txt">Story Definitions</A></td>
			            		<td>For each story, a description of what it is and other relevant data.</td>
				            </tr>
			            	<tr>
				            	<td><A href = "download.php?what=themedefinitions&fmt=txt">Theme Definitions</A></td>
			            		<td>For each theme, the definition of the theme and other relevant data.</td>
				            </tr>
				            <tr>
			            		<td><A href = "download.php?what=storythemes&fmt=txt">Themes in Stories</A></td>
			            		<td>For each story, all themes that have been assigned to it along with notes and comments.</td>
			            	</tr>
			            	</tbody>
	            	</TABLE>
            	</div>
            </div>
        </div>


        <div class="col-sm-12 col-md-8 col-lg-6">
			<div class="panel panel-default">
				<div class="panel-body">
	              	<H3 class="px-3">API</H3>
	            	<TABLE class="table table-striped">
		            	<tbody>
			            	<tr>
				            	<td><A href = "json.php?action=metathemedata">Full Theme/Metatheme usage and hierarchy data</A></td>
			            		<td>
			            			Five items will be returned:
			            			<ol>
			            			<li>A mapping from leaf_theme to list of [sid, weight] tuples, indicating when a theme was directly used.</li>
			            			<li>A mapping from meta_theme to list of [sid, weight] tuples, indicating when a theme was indirectly used.</li>
			            			<li>A mapping from child_theme to parent_theme, indicating the hierarchy.</li>
			            			<li>A mapping from parent_theme to child_theme, indicating the hierarchy.</li>
			            			<li>A list of "top" level themes, i.e., those that have no parents.</li>
			            			</ol>
			            		</td>
				            </tr>
			            	<tr>
				            	<td><A href = "json.php?action=storydefinitions">Full list of stories</A></td>
			            		<td>
			            			Same as the csv download but in JSON format. 
			            			First row will contain headers. 
			            			The data will contain story id, title, date, and description. 
			            			Other columns may be added.
			            			We will try not to remove or rename columns.
			            		</td>
				            </tr>
			            	<tr>
				            	<td><A href = "json.php?action=themedefinitions">Full list of themes</A></td>
			            		<td>
			            			Same as the csv download but in JSON format. 
			            			First row will contain headers. 
			            			The data will contain theme name, description and parents. 
			            			Other columns may be added.
			            			We will try not to remove or rename columns.
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
