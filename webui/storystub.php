<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<?php 
	$SID = $_GET['name'];
?>
<head>
	<meta charset="UTF-8">
	<title>Theme Ontology <?php echo $SID; ?></title>

<?php include "header.php"; ?>
    <script>
        var g_objType = "story";
        var g_objName = "<?php echo $SID; ?>";
        var g_objFields = [ "name", "title", "date", "description" ];

        var g_objDefs = {
        	"main" : {
        		"type" : "story",
        		"name" : "<?php echo $SID; ?>",
        		"fields" : [ "name", "title", "date", "description" ],
        	},
        	"theme" : {
        		"type" : "story",
        		"name" : "<?php echo $SID; ?>",
        		"fields" : [ "name", "title", "date", "description" ],
        	},

        };
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
                        <div style="float:right;"><H4><span class="label label-story">story</span></H4></div>
                        <H4><?php echo $SID; ?></H4>
                    </div>
                    <div class="panel-body">
                        <dl class="dl-horizontal text-left">
                            <dt>Title:</dt> <dd><span id="obj_title"></span></dd>
                            <dt>Date:</dt> <dd><span id="obj_date"></span></dd>
                        </dl>
                        <P>
                            <div id="div_description"></div>
                        </P>
                    </div>
                </div>
            </div>
        </div>
    </div>

</body>
</html>
