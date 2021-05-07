<?php /* Template Name: Map */ ?>

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Map</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script async
        src="https://maps.googleapis.com/maps/api/js?key=">
    </script>
    <style>
        #map {
            height: 80%;
        }

        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
        }

        #filter-buttons {
            padding: 10px;
        }

        .btn {
            border: none;
            outline: none;
            padding: 12px 16px;
            background-color: #f1f1f1;
            cursor: pointer;
        }

        #state-div,
        #open-date-div,
        #coordinates-div {
            display: inline-block;
        }
    </style>
</head>
<body>
    <script>
        let markers = [];
        let map;

        function addMarkers(data) {
            for (const index in data) {
                let point = data[index];
                const contentString = `
                    <b>Name: </b>${point.station_name}
                    <br>
                    <b>City: </b>${point.city}
                    <br>
                    <b>State: </b>${point.state}
                    <br>
                    <b>Open date: </b>${point.open_date}
                `;
                const infowindow = new google.maps.InfoWindow({
                    content: contentString,
                });
                
                let marker = new google.maps.Marker({
                    position: new google.maps.LatLng(point.latitude, point.longitude),
                    title: point.id,
                    map: map
                });
                marker.addListener("click", () => {
                    infowindow.open(map, marker);
                });
                markers.push(marker);
            }                
        }

        function setMarkers(map) {
            for (let i = 0; i < markers.length; i++) {
                markers[i].setMap(map);
            }
        }

        function getCount() {
            $.ajax({
                type: 'GET',
                url: '/index.php/data?count=1',
                dataType: 'json',
                success: function (data) {
                    $("#count").text(data.count);
                    for (let index = 0; index < data.count/1000; index++) {
                        let query = 'part=' + index;
                        getData(query, false);
                    }
                },
            });
        }

        function getData(query, set=true) {
            $.ajax({
                type: 'GET',
                url: '/index.php/data?' + query,
                dataType: 'json',
                success: function (data) {
                    addMarkers(data);
                    if (set) {
                        $("#count").text(data.length);
                    }
                }
            });
        }

        function getCities() {
            $.ajax({
                type: 'GET',
                url: '/index.php/data?cities=1',
                dataType: 'json',
                success: function (data) {
                    data.forEach((city) => {
                        cities.push(city.city);
                    })
                }
            });
        }

        function filter() {
            setMarkers(null);
            markers = [];
            let query = 'state=' + $("#state").val() + '&city=' + $("#state-city").val() + 
                        '&open-date-start=' + $("#open-date-start").val() + '&open-date-end=' + $("#open-date-end").val() + 
                        '&latitude=' + $("#coordinates-latitude").val() + '&longitude=' + $("#coordinates-longitude").val();
            getData(query);
        }

        function showAll() {
            setMarkers(null);
            markers = [];
            getCount();
        }

        let cities = [];

        $(document).ready(function () {
            setTimeout(function() {
                map = new google.maps.Map(document.getElementById('map'), {
                    center: {lat: 39.793487, lng: -99.242224},
                    zoom: 4.7
                });
            }, 100);
            getCities();
            $( "#state-city" ).autocomplete({
                source: cities
            });
        });
    </script>
    <div id="filter-buttons">
        State: 
        <div id="state-div">
            <select name="state" id="state">
                <option value=""></option>
                <option value="AL">Alabama</option>
                <option value="AK">Alaska</option>
                <option value="AZ">Arizona</option>
                <option value="AR">Arkansas</option>
                <option value="CA">California</option>
                <option value="CO">Colorado</option>
                <option value="CT">Connecticut</option>
                <option value="DE">Delaware</option>
                <option value="DC">District Of Columbia</option>
                <option value="FL">Florida</option>
                <option value="GA">Georgia</option>
                <option value="HI">Hawaii</option>
                <option value="ID">Idaho</option>
                <option value="IL">Illinois</option>
                <option value="IN">Indiana</option>
                <option value="IA">Iowa</option>
                <option value="KS">Kansas</option>
                <option value="KY">Kentucky</option>
                <option value="LA">Louisiana</option>
                <option value="ME">Maine</option>
                <option value="MD">Maryland</option>
                <option value="MA">Massachusetts</option>
                <option value="MI">Michigan</option>
                <option value="MN">Minnesota</option>
                <option value="MS">Mississippi</option>
                <option value="MO">Missouri</option>
                <option value="MT">Montana</option>
                <option value="NE">Nebraska</option>
                <option value="NV">Nevada</option>
                <option value="NH">New Hampshire</option>
                <option value="NJ">New Jersey</option>
                <option value="NM">New Mexico</option>
                <option value="NY">New York</option>
                <option value="NC">North Carolina</option>
                <option value="ND">North Dakota</option>
                <option value="OH">Ohio</option>
                <option value="OK">Oklahoma</option>
                <option value="OR">Oregon</option>
                <option value="PA">Pennsylvania</option>
                <option value="RI">Rhode Island</option>
                <option value="SC">South Carolina</option>
                <option value="SD">South Dakota</option>
                <option value="TN">Tennessee</option>
                <option value="TX">Texas</option>
                <option value="UT">Utah</option>
                <option value="VT">Vermont</option>
                <option value="VA">Virginia</option>
                <option value="WA">Washington</option>
                <option value="WV">West Virginia</option>
                <option value="WI">Wisconsin</option>
                <option value="WY">Wyoming</option>
            </select>
            <label for="state-city">City: </label>
            <input type="text" id="state-city">
        </div>
        <br>
        Open date: 
        <div id="open-date-div">
            <label for="open-date-start">From: </label>
            <input type="date" id="open-date-start">
            <label for="open-date-end">To: </label>
            <input type="date" id="open-date-end">
        </div>
        <br>
        <div id="coordinates-div">
            <label for="coordinates-latitude">Latitude: </label>
            <input type="number" id="coordinates-latitude">
            <label for="coordinates-longitude">Longitude: </label>
            <input type="number" id="coordinates-longitude">
        </div>
        <br>
        <button onclick="filter()">Filter</button>
    </div>
    <button class="btn" onclick="showAll()">Show All</button>
    <span id="count">0</span>
    <div id="map"></div>
</body>
</html>
