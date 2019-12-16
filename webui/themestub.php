<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<?php
	$THEME = $_GET['name'];
    $THME_URL = urlencode($THEME);
?>
<head>
	<meta charset="UTF-8">
	<title>Theme Ontology theme: <?php echo $THEME; ?></title>

<?php include "header.php"; ?>
    <script>
        var g_objType = "theme";
        var g_objName = "<?php echo $THEME; ?>";
        var g_objFields = [ "name", "title", "description" ];
        var g_objInfoBoxes = [ "parents", "children" ];
    	var g_objData;
    </script>
    <script type="text/javascript" src="js/tstp_objinfo.js"></script>
</head>

<body style="padding: 0px; margin:0px; background-color: transparent;">
<div class="container main-body">
<?php // Basic information //?>
    <div class="row">
        <div id="div_maininfo" class="basebox">
            <div class="col-md-12">
                <div class="panel panel-default" style="box-shadow: 0 0 10px;">
                    <div class="panel-heading">
                        <div style="float:right;"><H4><span class="label label-theme">theme</span></H4></div>
                        <H4><?php echo $THEME; ?></H4>
                    </div>
                    <div class="panel-body"><div id="div_description"></div></div>
                </div>
            </div>
        </div>
    </div>

</body>
</html>
