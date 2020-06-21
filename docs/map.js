/**
 * 
 */

var region = "SL";

/*
 *  Utilitary stuff
 */

function getJsonObject(url,cb){
    // read text from URL location
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.send(null);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            var type = request.getResponseHeader('Content-Type');
            try {
              cb(JSON.parse(request.responseText));
            }catch(err) {
              console.log(err);
            }
        }
    }
}

function make_icon_label(icon_file, label){
	return new L.DivIcon({
        className: 'my-div-icon',
        html: '<img class="icon-image" src="./resources/icons/'+icon_file+'"/>'+
              '<div class="icon-label">'+label+'</div>'
    });
}


var map = L.map('mapid', {
    crs: L.CRS.Simple,
    minZoom: -5
});

map.setView( [0, 0], 0);

// var geojsonRoomOptions = {
// 	    opacity: 1,
// 	    zIndex: 1
// 	};

var current_difficulty = 0;
var difficulties_names = {
		0:"survivor",
		1:"monk",
		2:"hunter",
		}
var difficulties_icons = {
		0:"17_slugcat.png",
		1:"65_monk.png",
		2:"64_hunter.png",
		}

//Difficulties show up
difficulty_filters = {
    0: function (feature, featureLayer) { return feature.properties.difficulties.includes(0); },
    1: function (feature, featureLayer) { return feature.properties.difficulties.includes(1); },
    2: function (feature, featureLayer) { return feature.properties.difficulties.includes(2); },
}


function show_difficulty(new_difficulty) {
    current_difficulty = new_difficulty;
    spawn_show_difficulty(current_difficulty);
    // ...
}


// Rooms
function room_to_map(feature, latlng){
	var latlng_topright = L.latLng([latlng.lat + feature.properties.size[1], latlng.lng + feature.properties.size[0]]);
	return L.imageOverlay(feature.properties.file, [latlng, latlng_topright]);
}

function room_name_to_map(feature, latlng) {
	var label = String(feature.properties.name);
	var title_pos = L.latLng([latlng.lat + feature.properties.size[1], latlng.lng + feature.properties.size[0]/2]);
	return L.marker(title_pos,{ opacity: 0 }).bindTooltip(label, {permanent: true, direction: "center", className: "room-labels"}).openTooltip();
}

var roomStyle = { "opacity": 1 };


// Throwables
function throwable_to_layer(feature, latlng) {
    return L.marker(latlng, { icon: L.icon({ iconUrl: './resources/icons/' + feature.properties.icon, }) });
}


//Creature Spawns
var spawn_difficulty_layers = {};
function spawn_show_difficulty(difficulty) {
    for (key in spawn_difficulty_layers) {
        if (key == difficulty) {
            map.addLayer(spawn_difficulty_layers[key]);
        } else {
            map.removeLayer(spawn_difficulty_layers[key]);
        }
    }
}

function spawn_to_layer(feature, latlng) {
    if (!feature.properties.is_lineage) {
        // return L.marker(latlng, {icon:L.icon({iconUrl:'./resources/icons/' + feature.properties.creature_icon, iconSize:[50,50],iconAnchor:[25,25]})});
        return L.marker(latlng, { icon: make_icon_label(feature.properties.creature_icon, "x" + feature.properties.amount) });
    } else {
        var icons = [];
        for (var i = 0; i < feature.properties.lineage_icons.length; i++) {
            //icons.push(L.icon({iconUrl:'./resources/icons/' + feature.properties.lineage_icons[i], iconSize:[50,50],iconAnchor:[25,25]}));
            icons.push(make_icon_label(feature.properties.lineage_icons[i], "" + feature.properties.lineage_probs[i]));
        }
        return L.marker.stack(latlng, { icons: icons, stackOffset: [0, 20] });
    }
}


function load_region(region) {
    // Clear all
    map.eachLayer(function (layer) {
        map.removeLayer(layer);
    });


    // Rooms
    getJsonObject("./resources/" + region + "/" + region + "_rooms.geojson", function (geojsonFeature) {
        L.geoJSON(geojsonFeature, { pointToLayer: room_to_map, style: roomStyle }).addTo(map);
        L.geoJSON(geojsonFeature, { pointToLayer: room_name_to_map, style: roomStyle }).addTo(map);
    });

    // Connections
    getJsonObject("./resources/" + region + "/" + region + "_connections.geojson", function (geojsonFeature) {
        L.geoJSON(geojsonFeature, { style: roomStyle }).addTo(map);
    });

    // Throwables
    getJsonObject("./resources/" + region + "/" + region + "_throwables.geojson", function (geojsonFeature) {
        L.geoJSON(geojsonFeature, { pointToLayer: throwable_to_layer, style: roomStyle }).addTo(map);
    });

    //Creature Spawns
    getJsonObject("./resources/" + region + "/" + region + "_spawns.geojson", function (geojsonFeature) {
        spawn_difficulty_layers[0] = L.geoJSON(geojsonFeature, { pointToLayer: spawn_to_layer, filter: difficulty_filters[0], style: roomStyle }).addTo(map);
        spawn_difficulty_layers[1] = L.geoJSON(geojsonFeature, { pointToLayer: spawn_to_layer, filter: difficulty_filters[1], style: roomStyle }).addTo(map);
        spawn_difficulty_layers[2] = L.geoJSON(geojsonFeature, { pointToLayer: spawn_to_layer, filter: difficulty_filters[2], style: roomStyle }).addTo(map);
        spawn_show_difficulty(current_difficulty);
    });

}


load_region("SU")




