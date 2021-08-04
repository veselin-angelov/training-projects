<?php
    $values = [];

    while ("END\n" !== ($line = fgets(STDIN))) {
       $values[] = substr($line, 0, -1);
    }

    $_SERVER["GATEWAY_INTERFACE"] = "CGI/1.1";
    $_SERVER["SERVER_PROTOCOL"] = "HTTP/1.1";
    $_SERVER["SERVER_NAME"] = "localhost";
    $_SERVER["SERVER_PORT"] = "3000";
    $_SERVER["PATH_INFO"] = $values[0];
    $_SERVER["REQUEST_METHOD"] = $values[1];
    $_SERVER["QUERY_STRING"] = $values[2];

    if ($_SERVER["QUERY_STRING"] != 'undefined') {
        foreach (explode('&', $_SERVER["QUERY_STRING"]) as $chunk) {
            $param = explode("=", $chunk);
            if ($param) {
                $_GET[urldecode($param[0])] = intval(urldecode($param[1]));
            }
        }
    }

    if ($values[3] != 'undefined') {
        $temp = json_decode($values[3], True);
        foreach ($temp as $key=>$value) {
            $_POST[$key] = $value;
        }
    }

    switch($_SERVER['REQUEST_METHOD']) {
        case 'GET':
            $_REQUEST[] = &$_GET;
            break;
        case 'POST':
            $_REQUEST[] = &$_POST;
            $_REQUEST[] = &$_GET;
            break;
        default:
            break;
    }

    include substr($_SERVER["PATH_INFO"], 2);
?>