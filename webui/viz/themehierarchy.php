<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>TSTP Theme Hierarchy</title>

    <style>
        body {
            font-family: sans-serif;
            margin: 0px;
            margin-bottom: 20em;
            padding: 1em;
        }

        h1 {
            margin-top: 3em;
            margin-bottom: 0em;
        }

        h2 {
            margin-top: 0.75em;
            margin-bottom: 0.25em;
        }

        A {
            color: #000000;
            text-decoration: none;
        }
        A:hover {
            color: #CC0000;
            text-decoration: underline;
        }

        table {
            background: #f0f0f0;
            border-collapse: collapse;
        }

        th {
            background: #f0f0f0;
            border: 2px solid white;
        }

        td {
            background: #ffffff;
            border: 0px solid black;
            vertical-align: top;
        }

        div.headingbox {
            background: black;
            color: white;
            padding: 1em;
        }

    </style>
</head>

<body>

<div class="container main-body headingbox">
    <div class="row">
        <H3>TSTP Theme Hierarchy Reference Sheet</H3>
    </div>
</div>

<div class="container main-body">
    <div class="row">
<?php
require_once("../pythonlib.php");
chdir("../../scripts");
echo tstp_simple_run('pyrun viz.themehierarchy 2>/dev/null');
?>
    </div>
</div>
</body>
</html>
