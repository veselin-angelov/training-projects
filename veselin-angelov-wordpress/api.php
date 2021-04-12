<?php /* Template Name: API data */

    global $wpdb;
    // "AL", "AK", "AZ", "AR", "CA",  

    $states = array("CO", "CT", "DC", "DE", "FL", "GA", 
                    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
                    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
                    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
                    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY");

    for ($i = 0; $i < count($states); $i++) {
        $url = 'https://developer.nrel.gov/api/alt-fuel-stations/v1.json?api_key=sqNKgMX0LTp2sDcdzJ1Pjf1ziNE4cel8vev9AU5p&state='.$states[$i];
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $data = curl_exec($ch);
        curl_close($ch);
        $data_array = json_decode($data, true);
        $fuel_stations = $data_array['fuel_stations'];
        // print("<pre>".print_r ($fuel_stations, true)."</pre>");
        for ($x = 0; $x < count($fuel_stations); $x++) {
            // print("<pre>".print_r($fuel_stations[$x]['latitude'].", ".$fuel_stations[$x]['longitude'] ,true)."</pre>");
            $wpdb->query(
                $wpdb->prepare(
                "
                INSERT INTO locations
                (access_days_time,access_detail_code,cards_accepted,date_last_confirmed,expected_date,fuel_type_code,groups_with_access_code,access_code,open_date,owner_type_code,status_code,station_name,station_phone,updated_at,facility_type,geocode_status,latitude,longitude,city,intersection_directions,plus4,state,street_address,zip,country,bd_blends,cng_dispenser_num,cng_fill_type_code,cng_psi,cng_renewable_source,cng_total_compression,cng_total_storage,cng_vehicle_class,e85_blender_pump,e85_other_ethanol_blends,ev_connector_types,ev_dc_fast_num,ev_level1_evse_num,ev_level2_evse_num,ev_network,ev_network_web,ev_other_evse,ev_pricing,ev_renewable_source,hy_is_retail,hy_pressures,hy_standards,hy_status_link,lng_renewable_source,lng_vehicle_class,lpg_primary,lpg_nozzle_types,ng_fill_type_code,ng_psi,ng_vehicle_class,access_days_time_fr,intersection_directions_fr,bd_blends_fr,groups_with_access_code_fr,ev_pricing_fr)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %f, %f, %s, %s, %s, %s, %s, %d, %s, %s, %d, %s, %s, %s, %d, %d, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ",
                array(
                    $fuel_stations[$x]['access_days_time'],
                    $fuel_stations[$x]['access_detail_code'],
                    $fuel_stations[$x]['cards_accepted'],
                    $fuel_stations[$x]['date_last_confirmed'],
                    $fuel_stations[$x]['expected_date'],
                    $fuel_stations[$x]['fuel_type_code'],
                    $fuel_stations[$x]['groups_with_access_code'],
                    $fuel_stations[$x]['access_code'],
                    $fuel_stations[$x]['open_date'],
                    $fuel_stations[$x]['owner_type_code'],
                    $fuel_stations[$x]['status_code'],
                    $fuel_stations[$x]['station_name'],
                    $fuel_stations[$x]['station_phone'],
                    $fuel_stations[$x]['updated_at'],
                    $fuel_stations[$x]['facility_type'],
                    $fuel_stations[$x]['geocode_status'],
                    $fuel_stations[$x]['latitude'],
                    $fuel_stations[$x]['longitude'],
                    $fuel_stations[$x]['city'],
                    $fuel_stations[$x]['intersection_directions'],
                    $fuel_stations[$x]['plus4'],
                    $fuel_stations[$x]['state'],
                    $fuel_stations[$x]['street_address'],
                    $fuel_stations[$x]['zip'],
                    $fuel_stations[$x]['country'],
                    $fuel_stations[$x]['bd_blends'],
                    $fuel_stations[$x]['cng_dispenser_num'],
                    $fuel_stations[$x]['cng_fill_type_code'],
                    $fuel_stations[$x]['cng_psi'],
                    $fuel_stations[$x]['cng_renewable_source'],
                    $fuel_stations[$x]['cng_total_compression'],
                    $fuel_stations[$x]['cng_total_storage'],
                    $fuel_stations[$x]['cng_vehicle_class'],
                    $fuel_stations[$x]['e85_blender_pump'],
                    $fuel_stations[$x]['e85_other_ethanol_blends'],
                    $fuel_stations[$x]['ev_connector_types'],
                    $fuel_stations[$x]['ev_dc_fast_num'],
                    $fuel_stations[$x]['ev_level1_evse_num'],
                    $fuel_stations[$x]['ev_level2_evse_num'],
                    $fuel_stations[$x]['ev_network'],
                    $fuel_stations[$x]['ev_network_web'],
                    $fuel_stations[$x]['ev_other_evse'],
                    $fuel_stations[$x]['ev_pricing'],
                    $fuel_stations[$x]['ev_renewable_source'],
                    $fuel_stations[$x]['hy_is_retail'],
                    $fuel_stations[$x]['hy_pressures'],
                    $fuel_stations[$x]['hy_standards'],
                    $fuel_stations[$x]['hy_status_link'],
                    $fuel_stations[$x]['lng_renewable_source'],
                    $fuel_stations[$x]['lng_vehicle_class'],
                    $fuel_stations[$x]['lpg_primary'],
                    $fuel_stations[$x]['lpg_nozzle_types'],
                    $fuel_stations[$x]['ng_fill_type_code'],
                    $fuel_stations[$x]['ng_psi'],
                    $fuel_stations[$x]['ng_vehicle_class'],
                    $fuel_stations[$x]['access_days_time_fr'],
                    $fuel_stations[$x]['intersection_directions_fr'],
                    $fuel_stations[$x]['bd_blends_fr'],
                    $fuel_stations[$x]['groups_with_access_code_fr'],
                    $fuel_stations[$x]['ev_pricing_fr'],
                )
                )
            );
        }
        echo 'ok';
    }
?>
