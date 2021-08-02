<?php
    $_SERVER["GATEWAY_INTERFACE"] = "CGI/1.1";
    $_SERVER["SERVER_PROTOCOL"] = "HTTP/1.1";
    $_SERVER["SERVER_NAME"] = "localhost";
    $_SERVER["SERVER_PORT"] = "3000";
    $_SERVER["PATH_INFO"] = $argv[1];
    $_SERVER["REQUEST_METHOD"] = $argv[2];
    $_SERVER["QUERY_STRING"] = $argv[3];

    if ($_SERVER["QUERY_STRING"] != 'undefined') {
        foreach (explode('&', $_SERVER["QUERY_STRING"]) as $chunk) {
            $param = explode("=", $chunk);
            if ($param) {
                $_GET[urldecode($param[0])] = intval(urldecode($param[1]));
            }
        }
    }

    if ($argv[4] != 'undefined') {
        $temp = json_decode($argv[4], True);
        foreach ($temp as $key=>$value) {
            $_POST[$key] = $value;
        }
    }

    switch($_SERVER['REQUEST_METHOD']) {
        case 'GET':
            $_REQUEST = &$_GET;
            break;
        case 'POST':
            $_REQUEST = &$_POST;
            break;
        default:
            break;
    }

    include substr($argv[1], 2);
?>