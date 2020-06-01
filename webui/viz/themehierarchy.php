<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>Theme Hierarchy</title>

    <style>
        body {
            font-family: sans-serif;
            margin: 0px;
            margin-bottom: 20em;
            padding: 1em;
        }

        h1 {
            background: #c0c0c0;
            border-bottom: 3px solid black;
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
            padding: 0.5em;
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
        }

    </style>
</head>

<body style="padding:0px;">

<div class="container main-body headingbox">
    <div class="row">
        <H3>Theme Hierarchy Reference Sheet</H3>
    </div>
</div>

<div class="container main-body">
    <div class="row">
<?php
require_once("../pythonlib.php");
echo tstp_pyrun('viz.themehierarchy 2>&1');
?>
    </div>
</div>
</body>
</html>
