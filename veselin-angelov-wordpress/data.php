<?php /* Template Name: Data */ 
    global $wpdb;

    $filters = array();
    $query = $_SERVER['QUERY_STRING'];
    $query = explode('&', $query);

    for ($i = 0; $i < count($query); $i++) {
        $filter = explode('=', $query[$i]);
        $filters[$filter[0]] = $filter[1];
    }

    if ($filters['state']) {
        $q = "SELECT * FROM locations WHERE state='{$filters['state']}' AND city LIKE '%{$filters['city']}%';";
        $locations = $wpdb->get_results($q);
        echo json_encode($locations);
    }

    if ($filters['open-date-start'] && $filters['open-date-end']) {
        $q = "SELECT * FROM locations WHERE open_date BETWEEN '{$filters['open-date-start']}' AND '{$filters['open-date-end']}';";
        $locations = $wpdb->get_results($q);
        echo json_encode($locations);
    }

    if ($filters['latitude'] && $filters['longitude']) {
        $q = "SELECT * FROM locations WHERE latitude LIKE '{$filters['latitude']}%' AND longitude LIKE '{$filters['open-date-end']}%';";
        // echo $q;
        $locations = $wpdb->get_results($q);
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
