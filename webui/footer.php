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
			 | <A href="util">util</A>
			 | <A href="log">log</A>

<?php if ($_SERVER["SERVER_PORT"] == "8080") { ?>
			 | <A href="http://www.themeontology.org/">prod</A>
<?php } else { ?>
			 | <A href="http://www.themeontology.org:8080/tstp/webui/">uat</A>
<?php } ?>

		</p>
	</div>
</footer>

<script src="VisualCaptcha/public/js/visualcaptcha.jquery.js"></script>

