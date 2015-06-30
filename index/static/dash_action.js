var addedPunc = false;

function add_punc(){
	if(!addedPunc){
		document.getElementById("new_jack_box").innerHTML += ',&nbsp;';
		addedPunc = true;

		jack_box = document.getElementById("new_jack_box");
		setEndOfContenteditable(jack_box);
	}
}

function textChange(){
	//var contenteditable = document.querySelector('[contenteditable]'),
	text = document.getElementById("new_jack_box").textContent;
	document.getElementById("new_jack_post_box").value = text;
	usedChars = text.length;
	document.getElementById("remaining_chars").innerHTML = (usedChars + '/160');
}

function setEndOfContenteditable(contentEditableElement){
	var range,selection;
	if(document.createRange){ //Firefox, Chrome, Opera, Safari, IE 9+
		range = document.createRange();//Create a range (a range is a like the selection but invisible)
		range.selectNodeContents(contentEditableElement);//Select the entire contents of the element with the range
		range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
		selection = window.getSelection();//get the selection object (allows you to change selection)
		selection.removeAllRanges();//remove any selections already made
		selection.addRange(range);//make the range you have just created the visible selection
	}
	else if(document.selection){ //IE 8 and lower
		range = document.body.createTextRange();//Create a range (a range is a like the selection but invisible)
		range.moveToElementText(contentEditableElement);//Select the entire contents of the element with the range
		range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
		range.select();//Select the range (make it the visible selection
	}
}

var mapCreated = false;
var geoEnabled = false;

function addLocation(){
	if (navigator.geolocation){
		navigator.geolocation.getCurrentPosition(showPosition);
	}else{
		document.getElementById("new_jack_box").textContent += "no geolocation";
	}
}

function createMap(mapCanvas, position_object){
	var MY_MAPTYPE_ID = 'custom_style';

	//and now display it on the page, using google maps
	longlat = new google.maps.LatLng(position_object["lat"], position_object["long"])
	var mapOptions = {
		center: longlat,
		zoom: 16,
		mapTypeControlOptions: {
			mapTypeIds: [google.maps.MapTypeId.ROADMAP, MY_MAPTYPE_ID]
		},
		mapTypeId: MY_MAPTYPE_ID,

		panControl: false,
		zoomControl: false,
		mapTypeControl: false,
		scaleControl: false,
		streetViewControl: false,
		overviewMapControl: false,
		disableDefaultUI: true
	}
	var map = new google.maps.Map(mapCanvas, mapOptions);

	var marker = new google.maps.Marker({
		position: longlat,
		map: map,
		//title: 'lmao'
	});

	var featureOpts = [
	{
		stylers: [
		{ visibility: 'simplified' },
		{ saturation: -100 },
		{ weight: 2 }
		]
	},
	{
		elementType: 'labels',
		stylers: [
		{ visibility: 'off' }
		]
	},
	{
		featureType: 'water',
		stylers: [
		{ color: '#888888' }
		]
	}
	];

	var styledMapOptions = {
		name: 'Custom Style'
	};
	var customMapType = new google.maps.StyledMapType(featureOpts, styledMapOptions);

	map.mapTypes.set(MY_MAPTYPE_ID, customMapType);
	mapCreated = true;
}

function showPosition(position) {
	geoEnabled = !geoEnabled
	if(geoEnabled){
		position_object = {
			"lat": position.coords.latitude,
			"long": position.coords.longitude
		}

		var mapCanvas = document.getElementById('geolocation_map');
		if(!mapCreated){
			createMap(mapCanvas, position_object);
		}

		json_pos = JSON.stringify(position_object);
		document.getElementById("jack_geo").value = json_pos;
		document.getElementById("geolocation_map").style.display = 'block';
		document.getElementById("location_button").children[0].innerHTML = "location_off";

	}else{
		document.getElementById("geolocation_map").style.display = 'none';
		document.getElementById("location_button").children[0].innerHTML = "location_on";
		document.getElementById("jack_geo").value = "";
	}
}

function useWebcam(){
	document.getElementById("camera_box").style['display'] = "block";
	Webcam.attach('#camera_view');
}
