<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>TSTP new story</title>
<?php include "header.php"; ?>
</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">

<?php // Basic information //?>
    <div class="row">
        <div class="col-md-12 hpad0">
                <form method="post" enctype="multipart/form-data">
                    <fieldset class="form-group">
                        <label for="importurl">Import from URL (copy&amp;paste Wikipedia link)</label>
                        <input id="importurl" type="text" class="form-control" autofocus 
                            onchange="scheduleReload()" oninput="scheduleReload()">
                    </fieldset>

                    <fieldset class="form-group">
                        <label for="fieldTitle">Story ID</label>
                        <input id="fieldTitle" type="text" class="form-control" OnChange="updateOutput()">
                    </fieldset>

                    <fieldset class="form-group form-inline">
                        <label for="fieldGenre" class="checkbox-inline">Genre</label>
                        <input id="fieldGenre" type="checkbox" OnChange="updateOutput()">
                        <label for="fieldRatings" class="checkbox-inline">Ratings</label>
                        <input id="fieldRatings" type="checkbox" OnChange="updateOutput()">
                    </fieldset>

                    <fieldset class="form-group">
                        <label for="fieldTitle">Story Definition</label>
                        <textarea class="form-control" style="height:95%;" rows=20 id="rawentry"></textarea>
                    </fieldset>
                    

                </form>
        </div>
    </div>
</div>

<?php include "footer.php"; ?>
</body>
</html>
