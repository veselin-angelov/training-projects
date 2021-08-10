<?php
    function readTheFile($path) {
        $handle = fopen($path, "r");

        while(!feof($handle)) {
            echo trim(fgets($handle));
        }

        fclose($handle);
    }
?>