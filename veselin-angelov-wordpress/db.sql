CREATE TABLE IF NOT EXISTS locations(
   id                         INTEGER  NOT NULL PRIMARY KEY AUTO_INCREMENT
  ,access_days_time           VARCHAR(196)
  ,access_detail_code         VARCHAR(23)
  ,cards_accepted             VARCHAR(65)
  ,date_last_confirmed        DATE  NOT NULL
  ,expected_date              VARCHAR(30)
  ,fuel_type_code             VARCHAR(3) NOT NULL
  ,groups_with_access_code    VARCHAR(33) NOT NULL
  ,access_code                VARCHAR(7) NOT NULL
  ,open_date                  DATE 
  ,owner_type_code            VARCHAR(2) NOT NULL
  ,status_code                VARCHAR(1) NOT NULL
  ,station_name               VARCHAR(64) NOT NULL
  ,station_phone              VARCHAR(12)
  ,updated_at                 VARCHAR(20) NOT NULL
  ,facility_type              VARCHAR(18) NOT NULL
  ,geocode_status             VARCHAR(5) NOT NULL
  ,latitude                   NUMERIC(17,14) NOT NULL
  ,longitude                  NUMERIC(18,14) NOT NULL
  ,city                       VARCHAR(17) NOT NULL
  ,intersection_directions    VARCHAR(364)
  ,plus4                      VARCHAR(30)
  ,state                      VARCHAR(2) NOT NULL
  ,street_address             VARCHAR(32) NOT NULL
  ,zip                        INTEGER  NOT NULL
  ,country                    VARCHAR(2) NOT NULL
  ,bd_blends                  VARCHAR(30)
  ,cng_dispenser_num          INTEGER 
  ,cng_fill_type_code         VARCHAR(1) NOT NULL
  ,cng_psi                    VARCHAR(9) NOT NULL
  ,cng_renewable_source       VARCHAR(30)
  ,cng_total_compression      INTEGER 
  ,cng_total_storage          INTEGER 
  ,cng_vehicle_class          VARCHAR(2) NOT NULL
  ,e85_blender_pump           VARCHAR(30)
  ,e85_other_ethanol_blends   VARCHAR(30)
  ,ev_connector_types         VARCHAR(30)
  ,ev_dc_fast_num             VARCHAR(30)
  ,ev_level1_evse_num         VARCHAR(30)
  ,ev_level2_evse_num         VARCHAR(30)
  ,ev_network                 VARCHAR(30)
  ,ev_network_web             VARCHAR(30)
  ,ev_other_evse              VARCHAR(30)
  ,ev_pricing                 VARCHAR(30)
  ,ev_renewable_source        VARCHAR(30)
  ,hy_is_retail               VARCHAR(30)
  ,hy_pressures               VARCHAR(30)
  ,hy_standards               VARCHAR(30)
  ,hy_status_link             VARCHAR(30)
  ,lng_renewable_source       VARCHAR(30)
  ,lng_vehicle_class          VARCHAR(30)
  ,lpg_primary                VARCHAR(30)
  ,lpg_nozzle_types           VARCHAR(30)
  ,ng_fill_type_code          VARCHAR(1) NOT NULL
  ,ng_psi                     VARCHAR(9) NOT NULL
  ,ng_vehicle_class           VARCHAR(2) NOT NULL
  ,access_days_time_fr        VARCHAR(30)
  ,intersection_directions_fr VARCHAR(30)
  ,bd_blends_fr               VARCHAR(30)
  ,groups_with_access_code_fr VARCHAR(53) NOT NULL
  ,ev_pricing_fr              VARCHAR(30)
);

ALTER TABLE locations
ADD CONSTRAINT location_info UNIQUE (station_name, latitude, longitude, open_date, fuel_type_code, access_days_time, ev_pricing, ev_network, ev_level1_evse_num, ev_level2_evse_num, ev_dc_fast_num);
