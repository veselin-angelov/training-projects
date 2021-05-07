<?php /* Template Name: Data */ 
    global $wpdb;

    $filters = array();
    $query = $_SERVER['QUERY_STRING'];
    $query = explode('&', $query);

    for ($i = 0; $i < count($query); $i++) {
        $filter = explode('=', $query[$i]);
        $filters[$filter[0]] = $filter[1];
    }

    if ($filters['count']) {
        $count = $wpdb->get_var("SELECT COUNT(*) FROM locations;");
        $obj->count = $count;
        echo json_encode($obj);
    }

    else if ($filters['part'] != null) {
        $offset = $filters['part']*1000;
        $q = "SELECT * FROM locations LIMIT 1000 OFFSET {$offset};";
        $locations = $wpdb->get_results($q);
        echo json_encode($locations);
    }

    else if ($filters['cities']) {
        $q = "SELECT DISTINCT city FROM locations;";
        $locations = $wpdb->get_results($q);
        echo json_encode($locations);
    }
    
    else {
        $q = "SELECT * FROM locations WHERE";

        if ($filters['state']) {
            $q .= " state='{$filters['state']}' AND";
        }

        if ($filters['city']) {
            $filters['city'] = str_replace("%20", " ", $filters['city']);
            $q .= " city LIKE '%{$filters['city']}%' AND";
        }

        if ($filters['open-date-start'] && $filters['open-date-end']) {
            $q .= " open_date BETWEEN '{$filters['open-date-start']}' AND '{$filters['open-date-end']}' AND";
        }

        if ($filters['latitude'] && $filters['longitude']) {
            $latitude1 = $filters['latitude'] - 0.001;
            $latitude2 = $filters['latitude'] + 0.001;
            $longitude1 = $filters['longitude'] - 0.001;
            $longitude2 = $filters['longitude'] + 0.001;
            $q .= " latitude >= '$latitude1' AND latitude <= '$latitude2' AND longitude >= '$longitude1' AND longitude <= '$longitude2' AND";
        }

        $q = substr($q, 0, -4);
        $q .= ";";
        $locations = $wpdb->get_results($q);
        echo json_encode($locations);
    }
?>
 