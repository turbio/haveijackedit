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

function removeGeo(){
	geoEnabled = true;
	addLocation();
}

function addLocation(){
	geoEnabled = !geoEnabled
	if(geoEnabled){
		if (navigator.geolocation){
			navigator.geolocation.getCurrentPosition(showPosition);
		}else{
			document.getElementById("new_jack_box").textContent += "no geolocation";
		}

		document.getElementById("geolocation_map").style.display = 'flex';
		document.getElementById("geobox").style.display = 'block';
		document.getElementById("location_button").children[0].innerHTML = "location_off";
	}else{
		document.getElementById("geolocation_map").style.display = 'none';
		document.getElementById("geobox").style.display = 'none';
		document.getElementById("location_button").children[0].innerHTML = "location_on";
		document.getElementById("jack_geo").value = "";
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
	document.getElementById("geolocation_map").className = "";
}

picFromWebcam = false;

function useWebcam(){
	document.getElementById("camera_box").style['display'] = "block";
	Webcam.set({image_format: 'png'})
	Webcam.attach('#camera_view');
	picFromWebcam = true;
}

function captureImage(){
	Webcam.freeze()

	document.getElementById("cam_cap").style.display = "none";
	document.getElementById("cam_retry").style.display = "block";
	document.getElementById("cam_save").style.display = "block";
	//Webcam.snap(function(data_uri, canvas, context){
		////document.getElementById('my_result').innerHTML = canvas.;
	//});
}

function retryImage(){
	Webcam.unfreeze()

	document.getElementById("cam_cap").style.display = "block";
	document.getElementById("cam_retry").style.display = "none";
	document.getElementById("cam_save").style.display = "none";
}

function saveImage(){
	Webcam.snap(function(data_uri){
		showImage(data_uri);
	});
}

var dropzoneAdded = false;

function addImage(){
	document.getElementById("jack_add_picture").style.display = "flex";

	if(!dropzoneAdded){
		dropzoneAdded = true;

		var myDropzone = new Dropzone("div#jack_add_picture",
			{
				url: "/file/post",
				maxFilesize: 8,
				maxFiles: 1,
				acceptedFiles: "image/*",
				autoProcessQueue: false,
				//previewTemplate: ""
			});
	}
}

function removePicture(){
	if(imageAdded){
		hideImage();
	}else{
		if(picFromWebcam){
			document.getElementById("camera_box").style['display'] = "none";
			picFromWebcam = false;
			Webcam.reset();
		}else{
			document.getElementById("jack_add_picture").style.display = "none";
		}
	}
}

function addLink(){
	document.getElementById("jack_add_link").style.display = "block";
}
function removeLink(){
	document.getElementById("jack_add_link").style.display = "none";
}

function addBro(){
	document.getElementById("jack_add_bro").style.display = "block";
}
function removeBro(){
	document.getElementById("jack_add_bro").style.display = "none";
}

function uploadFromFS(){
	fileinput = document.getElementById("image_input");
	fileinput.click();

	fileinput.onchange = function(){
		showUploadedImage(this);
	};
}

function showUploadedImage(input){
	if (input.files && input.files[0]) {
		var reader = new FileReader();

		reader.onload = function(e){
			showImage(e.target.result);
		}

		reader.readAsDataURL(input.files[0]);
	}
}

var imageAdded = false;

function hideImage(){
	document.getElementById("add_pic_controls").style.display = "block";
	document.getElementById("selected_image").style.display = "none";
	document.getElementById("jack_add_picture").setAttribute("class", "empty_box");
	document.getElementById("jack_add_picture").style.height = "6em";
	document.getElementById("jack_add_picture").style.margin = ".5em";
	document.getElementById("image_data").value = "";
	imageAdded = false;
}

function showImage(imageData){
	document.getElementById("image_data").value = imageData;
	document.getElementById("add_pic_controls").style.display = "none";
	document.getElementById("selected_image").setAttribute("src", imageData);
	document.getElementById("selected_image").style.display = "block";
	document.getElementById("jack_add_picture").setAttribute("class", "jack_field");
	document.getElementById("jack_add_picture").style.height = "inherit";
	document.getElementById("jack_add_picture").style.margin = "0";
	imageAdded = true;
}
