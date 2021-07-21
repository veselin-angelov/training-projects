<?php
    echo 'Hello, World!';

    function readTheFile($path) {
        $handle = fopen($path, "r");

        while(!feof($handle)) {
            echo trim(fgets($handle));
        }

        fclose($handle);
    }

    readTheFile("./files/1gb.json");

    if (isset($_GET['a']) && isset($_GET['b']) && is_numeric($_GET['a']) && is_numeric($_GET['b'])) {
        echo $_GET['a'] + $_GET['b'];
    }

    if (isset($_POST['a']) && isset($_POST['b']) && is_numeric($_POST['a']) && is_numeric($_POST['b'])) {
        echo $_POST['a'] + $_POST['b'];
    }
?>