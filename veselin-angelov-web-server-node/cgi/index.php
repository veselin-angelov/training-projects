<?php
    if (!function_exists('readTheFile')){
        include "read_file.php";
    }

//     echo 'Hello, World!';

    readTheFile("./files/100mb.json");

    if (isset($_GET['a']) && isset($_GET['b']) && is_numeric($_GET['a']) && is_numeric($_GET['b'])) {
        echo $_GET['a'] + $_GET['b'];
        echo "\n";
    }

    if (isset($_POST['a']) && isset($_POST['b']) && is_numeric($_POST['a']) && is_numeric($_POST['b'])) {
        echo $_POST['a'] + $_POST['b'];
    }
?>