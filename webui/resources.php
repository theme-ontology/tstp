<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Theme Ontology resources</title>
<?php include "header.php"; ?>
</head>

<body>
<?php include "navbar.php"; ?>

<div class="container">
    <div class="row">
        <div class="panel-body">

            <H3 class="px-3">Data Exploration and Visualization</H3>
            <TABLE class="table table-striped">
                <tbody>
                    <tr>
                        <td><A href = "/gitlog">Project History</A></td>
                        <td>
                            A history of the project in two pictures and a table.
                        </td>
                    </tr>
                    <tr>
                        <td><A href = "/pub/tstpviz/">Assorted Auto-generated Charts</A></td>
                        <td>
                            Various views of the data that are generated as and when the database is updated.
                        </td>
                    </tr>
                    <tr>
                        <td><A href = "viz/dist-themeusage.html">Themes distribution</A></td>
                        <td>
                            Number of themes per story, stories per theme, etc.
                        </td>
                    </tr>
                    <tr>
                        <td><A href = "/pub/tstpviz/themehierarchy.html">Theme Hierarchy Reference Sheet</A></td>
                        <td>
                            Browser friendly tabular overview of all themes in the current hierarchy.
                        </td>
                    </tr>
                    <tr>
                        <td><A href = "/pub/tstpviz/animated_stories_by_year.gif">Animated Project Progress Over Time</A></td>
                        <td>
                            An animated version of how stories have been added over time.
                        </td>
                    </tr>
                </tbody>
            </TABLE>
        </div>

        <div class="panel-body">
            <H3 class="px-3">Helpful Tools & Links</H3>
            <TABLE class="table table-striped">
                <tbody>
                    <tr>
                        <td><A href="newstory">import story entries</A></td>
                        <td>Import story entries from Wikipedia and other supported sources.</td>
                    </tr>
                    <tr>
                        <td><A href = "https://github.com/theme-ontology/theming">https://github.com/theme-ontology/theming</A></td>
                        <td>The theme repository.</td>
                    </tr>
                    <tr>
                        <td><A href = "https://github.com/theme-ontology/theming/releases">https://github.com/theme-ontology/theming/releases</A></td>
                        <td>Versioned releases of the theme ontology.</td>
                    </tr>
                    <tr>
                        <td><A href = "https://cran.r-project.org/web/packages/stoRy/index.html">https://cran.r-project.org/web/packages/stoRy/index.html</A></td>
                        <td>R package using the hypergeometric test to identify over represented themes in a given story set.</td>
                    </tr>

                </tbody>
            </TABLE>
        </div>

		<div class="panel-body">
          	<H3 class="px-3">Download Latest Data</H3>
        	<TABLE class="table table-striped">
            	<tbody>
                    <tr>
                        <td><A href = "/pub/data/">Find versioned copies of the data as json files</A></td>
                        <td>
                            "dev" indicates the latest version which has been imported from git. It is the data that is live on this website.
                        </td>
                    </tr>
	            	</tbody>
        	</TABLE>
        </div>

        <div class="panel-body">
            <H3 class="px-3">Guides</H3>
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


<?php include "footer.php"; ?>

</body>
</html>
