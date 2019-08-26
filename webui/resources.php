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
                        <td><A href = "viz/themehierarchy.php">Theme Hierarchy Reference Sheet</A></td>
                        <td>
                            Browser friendly, tabular, overview of all themes in the current hierarchy.
                        </td>
                    </tr>
                    <tr>
                        <td><A href = "viz/stories-by-year.gif">Animated Project Progress Over Time</A></td>
                        <td>
                            An animated version of 
                            static all_stories_by_year.svg
                            <A href = "/pub/tstpviz/all_stories_by_year.svg">
                            <IMG width="80%" src="/pub/tstpviz/all_stories_by_year.svg"></A>
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
		            	<td><A href = "download.php?what=storydefinitions&fmt=txt">Story Definitions (txt)</A></td>
	            		<td>For each story, a description of what it is and other relevant data.</td>
		            </tr>
	            	<tr>
		            	<td><A href = "download.php?what=themedefinitions&fmt=txt">Theme Definitions (txt)</A></td>
	            		<td>For each theme, the definition of the theme and other relevant data.</td>
		            </tr>
		            <tr>
	            		<td><A href = "download.php?what=storythemes&fmt=txt">Themes in Stories (txt)</A></td>
	            		<td>For each story, all themes that have been assigned to it along with notes and comments.</td>
	            	</tr>
                    <tr>
                        <td><A href = "json.php?action=metathemedata">Full Theme/Metatheme usage and hierarchy data (json)</A></td>
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
                        <td><A href = "json.php?action=storydefinitions">Full list of stories (json)</A></td>
                        <td>
                            First row will contain headers. 
                            The data will contain story id, title, date, and description. 
                            Other columns may be added.
                            We will try not to remove or rename columns.
                        </td>
                    </tr>
                    <tr>
                        <td><A href = "json.php?action=themedefinitions">Full list of themes (json)</A></td>
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
