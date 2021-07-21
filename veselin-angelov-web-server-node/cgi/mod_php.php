<?php
//     echo var_dump($argv);
    $_SERVER["REQUEST_METHOD"] = $argv[3];
    if ($_SERVER["REQUEST_METHOD"] == 'GET') {
        if ($argv[2] != 'undefined') {
            foreach (explode('&', $argv[2]) as $chunk) {
                $param = explode("=", $chunk);

                if ($param) {
                    $_GET[urldecode($param[0])] = urldecode($param[1]);
                }
            }
        }
    }
    else if ($_SERVER["REQUEST_METHOD"] == 'POST') {
        if ($argv[2] != 'undefined') {
            $temp = json_decode($argv[2], True);
            foreach ($temp as $key=>$value) {
                $_POST[$key] = $value;
            }
        }
    }

    include substr($argv[1], 2);
?>