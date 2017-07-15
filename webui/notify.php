<?php 

if ( $_POST['payload'] ) 
{
    file_put_contents("/var/tmp/tstpnotify.payload", $_POST['payload']);
    shell_exec('sudo -u ec2-user /home/ec2-user/dev/tstp/scripts/run stagethemes.sh');
}

?>