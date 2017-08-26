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
			 | <A href=":79">prod</A>
<?php } else { ?>
			 | <A href=":8080/tstp/webui/">uat</A>
<?php } ?>

		</p>
	</div>
</footer>

<script src="VisualCaptcha/public/js/visualcaptcha.jquery.js"></script>

