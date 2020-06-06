<?php include 'favicon.html'; ?>

<meta name="viewport" content="width=device-width, initial-scale=1">

<link rel="stylesheet" type="text/css" href="DataTables/datatables.min.css"/>
<link rel="stylesheet" type="text/css" href="css/bootstrap.min.css">
<link rel="stylesheet" type="text/css" href="css/tstp.css">
<link rel="stylesheet" media="all" href="VisualCaptcha/public/css/visualcaptcha.css">

<script type="text/javascript" src="DataTables/jQuery-2.2.3/jquery-2.2.3.min.js"></script>
<script type="text/javascript" src="js/bootstrap.min.js"></script>
<script type="text/javascript" src="DataTables/datatables.js"></script>
<script type="text/javascript" src="js/typeahead.bundle.js"></script>
<script type="text/javascript" src="js/jquery.form.js"></script>
<script type="text/javascript" src="js/tstp_util.js"></script>

<script>
    String.prototype.hashCode = function() {
        var hash = 0, i, chr;
        if (this.length === 0) return hash;
        for (i = 0; i < this.length; i++) {
            chr   = this.charCodeAt(i);
            hash  = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
        }
        return hash;
    };

	String.prototype.capitalize = function() {
		return this.charAt(0).toUpperCase() + this.slice(1);
	}

    // replace href=":xxxx/relative/path" type specs
    function fixRelativePort(target)
    {
        if (target.tagName.toLowerCase() == 'a')
        {
            var href = target.getAttribute('href');
            if (href) {
                var port = href.match(/^:(\d+)(.*)/);
                if (port)
                {
                    if (target.port == "8080")
                    {
                        target.href = port[2];
                        target.port = String(parseInt(port[1]) + 1);
                    } 
                    else
                    {
                        target.href = port[2];
                        target.port = port[1];            
                    }
                }
            }
        }        
    }

    // delegate event for performance, and save attaching a million events to each anchor
    document.addEventListener('click', function(event) {
        fixRelativePort(event.target);
    }, false);

</script>

<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-131790483-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'UA-131790483-1');
</script>



