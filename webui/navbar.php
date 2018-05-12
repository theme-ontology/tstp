<?php
	$ME = basename($_SERVER['PHP_SELF']);

	function make_link($name)
	{
		global $ME;

		$known = array(
			"themeontology.org" => "index",
            "Stories" => "stories",
            "Themes" => "themes",
            "Resources" => "resources",

            "index.php" => "themeontology.org",
            "stories.php" => "Stories",
            "story.php" => "Stories",
            "themes.php" => "Themes",
            "theme.php" => "Themes",
            "resources.php" => "Resources",
		);

		$cls = ($known[$ME] == $name) ? "active" : "";
		$link = $known[$name];

		if ($name == "themeontology.org")
		{
            if ($cls != "active")
            {
			     echo "<a class=\"navbar-brand \" style=\"font-variant:small-caps;\" href=\"$link\">$name</a>\n";
            } else {
                 echo "<a class=\"active-navbar navbar-brand \" style=\"font-variant:small-caps;\" href=\"$link\">$name</a>\n";
             }
		} 
		else 
		{
            $acls = ($cls == "") ? "" : "active-navbar-item";
			echo "<li class=\"$cls\"><a class=\"$acls\" href=\"$link\">$name</a></li>\n";
		}
	}
?>

<script>
    $(document).ready(function () {
    	loadCaptchaOnReady();
    });

    function generateCaptcha()
    {
        var captchaEl = $( '#sample-captcha' ).visualCaptcha({
            imgPath: "VisualCaptcha/public/img/",
            captcha: {
                numberOfImages: 6,
                callbacks: {
                    loaded: function( captcha ) {
                        // Avoid adding the hashtag to the URL when clicking/selecting visualCaptcha options
                        $( '#sample-captcha a' ).on( 'click', function( event ) {
                            event.preventDefault();
                        });
                    }
                },
                routes: {
                    start: '/VisualCaptcha/public/start',
                    image: '/VisualCaptcha/public/image',
                    audio: '/VisualCaptcha/public/audio',
                },
            }
        } );
        var captcha = captchaEl.data( 'captcha' );
    }

    function updateLogin(successTally, lastAttempt)
    {
    	var failed = (typeof(lastAttempt) == "string" && !lastAttempt.startsWith('status=valid'));
    	var message = "";
    	var needed = 3;
		var ntg = (needed - successTally).toString() + " to go:"

    	if (successTally >= needed)
    		message = "Proceed, human.";
    	else if (failed)
    		message = "Close but no cigar. " + ntg;
    	else if (successTally == 0)
    		message = "Show that you are flesh and blood:";
    	else
    		message = "Again, " + ntg;

		$("#captchaGreeting").html(message);

    	if (successTally >= needed)
    	{
			$("#loginState").html("verified");
			$("#formCaptcha").hide();
	    	$('#formLogOut').show();
    	}
		else
		{
			generateCaptcha();
			$("#loginState").html("Login");
			$("#formCaptcha").show();
	    	$('#formLogOut').hide();
	    }
    }

    function logoutCaptcha()
    {
		$.getJSON( "VisualCaptcha/public/invalidate", function( data ) {
	    	updateLogin(0, 0);
		});	
    }

    function loadCaptchaOnReady() 
    {
    	$('#formLogOut').hide();
    	updateLogin(<?php echo (isset($_SESSION["captchaBalance"])) ? intval($_SESSION["captchaBalance"]) : 0; ?>, 0);
        $('#formCaptcha').ajaxForm({
        	"success" : function(responseText, statusText, xhr, $form) { 
        		tally = responseText[1];
        		status = responseText[0];
        		updateLogin(tally, status);
        	},
    	});
    }
</script>

<nav class="navbar navbar-default <?php echo (isset($floatnavbar) && $floatnavbar == true) ? "" : "navbar-fixed-top"; ?> ">
  <div class="container-fluid">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
<?php
	make_link("themeontology.org");
?>
    </div>

    <div id="navbar" class="collapse navbar-collapse">
      <ul class="nav navbar-nav">
<?php
	make_link("Stories");
    make_link("Themes");
    make_link("Resources");
?>
      </ul>

    <ul class="nav navbar-nav navbar-right">
    	<li class="dropdown">
	     	<a href="#" class="dropdown-toggle" data-toggle="dropdown"><span class="glyphicon glyphicon-log-in"></span> <span id="loginState">Login</span></a>

			<ul id="login-dp" class="dropdown-menu">
				<li>
					 <div class="row">
					 	<div class="col-md-12">

<?php // VisualCaptcha DIV /////////////////////////////////
////////////////////////////////////////////////////////////?>
            <div id="captchaWrapper" class="captcha-wrapper">
            	<p id="captchaGreeting">Show that you are flesh and blood:</p>

                <form id="formCaptcha" class="frm-sample" action="VisualCaptcha/public/try" method="post">
                    <div id="status-message"></div>
                    <div id="sample-captcha"></div>

                    <button type="submit" name="submit-bt" class="btn btn-primary btn-block submit">Verify...</button>
                </form>

                <button id="formLogOut" onclick="logoutCaptcha()" type="submit" name="submit-bt" class="btn btn-primary btn-block submit">Log Out</button>

            </div>
<?php // VisualCaptcha /DIV ////////////////////////////////
////////////////////////////////////////////////////////////?>


					 	</div>
					 </div>
				</li>
			</ul>
		</li>
    </ul>

    </div><!--/.nav-collapse -->
  </div>
</nav>

