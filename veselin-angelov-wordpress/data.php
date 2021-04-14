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
        $latitude1 = $filters['latitude'] - 0.001;
        $latitude2 = $filters['latitude'] + 0.001;
        $longitude1 = $filters['longitude'] - 0.001;
        $longitude2 = $filters['longitude'] + 0.001;
        $q = "SELECT * FROM locations WHERE latitude >= '$latitude1' AND latitude <= '$latitude2' AND longitude >= '$longitude1' AND longitude <= '$longitude2';";
        $locations = $wpdb->get_results($q);
        echo json_encode($locations);
    }

    if ($filters['count']) {
        $count = $wpdb->get_var("SELECT COUNT(*) FROM locations;");
        $obj->count = $count;
        echo json_encode($obj);
    }

    if ($filters['part'] != null) {
        $offset = $filters['part']*1000;
        $q = "SELECT * FROM locations LIMIT 1000 OFFSET {$offset};";
        $locations = $wpdb->get_results($q);
        echo json_encode($locations);
    }
?>
 