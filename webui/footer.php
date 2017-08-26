<footer class="footer">
	<div class="container">
		<p class="text-muted">

			<span class="label label-default"><?php
			echo basename($_SERVER['PHP_SELF']);
			//echo "\n-----\n";
			//var_dump($_SERVER);
			?></span>

			 <A href="upload">upload</A>
			 | <A href="resources">download</A>
			 | <A href="log">log</A>

<?php if ($_SERVER["SERVER_PORT"] == "8080") { ?>
<<<<<<< HEAD
			 | <A href="http://www.themeontology.org/">prod</A>
=======
			 | <A href=":79">prod</A>
>>>>>>> 559e4575665b9e9b24f3f1ee3b731a81ce328f82
<?php } else { ?>
			 | <A href="http://www.themeontology.org:8080/tstp/webui/">uat</A>
<?php } ?>

		</p>
	</div>
</footer>

<script src="VisualCaptcha/public/js/visualcaptcha.jquery.js"></script>

