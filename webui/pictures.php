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

    <!-- visualizations -->
        <div class="col-sm-12 col-md-8 col-lg-6">
			<div class="panel panel-default">
				<div class="panel-body">
	              	<H3 class="px-3">Data Exploration and Visualization</H3>
	            	<TABLE class="table table-striped">
		            	<tbody>
                            <tr>
                                <td><A href = "viz/dist-themeusage.html">Themes distribution</A></td>
                                <td>
                                    How many minor/major/choice themes are assigned to each story? 
                                    What are the most frequently used themes?
                                </td>
                            </tr>
                            <!--tr>
                                <td><A href = ":3838/shiny/">Story Simularity</A></td>
                                <td>Pick a story and see other stories that are thematically similar.</td>
                            </tr-->
                            <tr>
                                <td><A href = "viz/themecube.html">Star Trek tos/tas/tng Theme Domain Distribution</A></td>
                                <td>
                                    A case study of how themes are distributed between the three early Star Trek TV Series. 
                                    This delineates, to an extent, how the show changed over the years.
                                </td>
                            </tr>
                            <tr>
                                <td><A href = "viz/themehierarchy.php">Theme Hierarchy Reference Sheet</A></td>
                                <td>
                                    Overview of all themes in the current hierarchy.
                                </td>
                            </tr>
                        </tbody>
	            	</TABLE>
            	</div>
            </div>
        </div>


    <!-- introductory material -->
        <div class="col-sm-12 col-md-8 col-lg-6">
            <div class="panel panel-default">
                <div class="panel-body">
                    <H3 class="px-3">Introduction</H3>
                    <TABLE class="table table-striped">
                        <tbody>
                            <tr>
                                <td><A href = "data/how-to-theme-flowchart-extended.pdf">How to Theme, part I</A></td>
                                <td>Breakdown of all theme categories.</td>
                            </tr>
                            <tr>
                                <td><A href = "data/how-to-theme-flowchart.pdf">How to Theme, part II</A></td>
                                <td>How to choose between top level theme categories.</td>
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
