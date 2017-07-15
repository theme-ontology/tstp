<?php 

if ($_SERVER['HTTP_X_GITHUB_EVENT'] == 'push')
{
    file_put_contents("/var/tmp/tstpnotify.payload", $_POST['payload']);
    $res = shell_exec('sudo -u ec2-user /home/ec2-user/dev/tstp/scripts/run stagethemes.sh 2>&1');
    file_put_contents("/var/tmp/tstpnotify.result", $res, FILE_APPEND);
    echo "done";
}
echo "nothing to do";

?>