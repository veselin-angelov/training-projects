<?php /* Template Name: Data */ 
    global $wpdb;

    $filters = array();
    $query = $_SERVER['QUERY_STRING'];
    $query = explode('&', $query);

    for ($i = 0; $i < count($query); $i++) {
        $filter = explode('=', $query[$i]);
        $filters[$filter[0]] = $filter[1];
    }

    // print_r($filters);

    
    // print_r($count);
    // echo $count/1000;
    // for ($i = 0; $i < $count/10000; $i++) {
    //     // echo $i*1000;
    //     $offset = $i*10000;
    //     $locations = $wpdb->get_results("SELECT * FROM locations LIMIT 10000 OFFSET {$offset};");
    //     echo json_encode($locations);
    // }
    // $part = $_SERVER['QUERY_STRING'];
    // // $part = explode('=', $part);
    // print_r(json_encode($part, true), true);
    // echo $part[1];

    if ($filters['state']) {
        $locations = $wpdb->get_results("SELECT * FROM locations WHERE state='{$filters['state']}';");
        echo json_encode($locations);
    }

    if ($filters['count']) {
        $count = $wpdb->get_var("SELECT COUNT(*) FROM locations;");
        $obj->count = $count;
        echo json_encode($obj);
    }

    if ($filters['part']) {
        $offset = $filters['part']*1000;
        $locations = $wpdb->get_results("SELECT * FROM locations LIMIT 1000 OFFSET {$offset};");
        echo json_encode($locations);
    }
?>
