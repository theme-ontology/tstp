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
	              	<H3 class="px-3">Download Latest Data</H3>
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

	              	<H3 class="px-3">Frozen Versions</H3>
	              	<P>These .tsv files are described in the manual for 
	              		<A href="https://cran.r-project.org/web/packages/stoRy/index.html">the R package stoRy</A>.</P>
	            	<TABLE class="table table-striped">
		            	<tbody>
			            	<tr>
				            	<td><A href = "data/TO_v0.1.0.tsv">TO_v0.1.0.tsv</A></td>
			            		<td>Earlier version of the ontology.</td>
				            </tr>
			            	<tr>
				            	<td><A href = "data/TO_v0.1.1.tsv">TO_v0.1.1.tsv</A></td>
			            		<td>Earlier version of the ontology.</td>
				            </tr>
			            	<tr>
				            	<td><A href = "data/TO_v0.1.2.tsv">TO_v0.1.2.tsv</A></td>
			            		<td>Earlier version of the ontology.</td>
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
			            			First row will contain headers. 
			            			The data will contain story id, title, date, and description. 
			            			Other columns may be added.
			            			We will try not to remove or rename columns.
			            		</td>
				            </tr>
			            	<tr>
				            	<td><A href = "json.php?action=themedefinitions">Full list of themes</A></td>
			            		<td>
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
