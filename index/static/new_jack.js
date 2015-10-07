var addedPunc = false;
var imageAdded = false;
var dropzoneAdded = false;
var picFromWebcam = false;

var addBro = false;
var addLink = false;
var addPic = false;
var addTag = false;

var secondElement;
var minuteElement;
var hourElement;
var dayElement;

var seconds = 0;
var minutes = 0;
var hours = 0;
var days = 0;

function addNewTag(object, text){
	if(text != ""){
		text = text.replace(/^\s+|\s+$/g, '');
		$(object).data("currentTags").push(text);
		$("<div class=\"inserted_tag\">" + text + "</div>").insertBefore(object);
	}
}

function checkForTagRemoval(event){
	if((event.key == "Backspace" || event.keyCode == 8)
			&& this.value.length == 0
			&& $(this).data("currentTags").length > 0){
		$(this).prev('.inserted_tag').remove();
		$(this).data("currentTags").pop();
	}
}

function checkForTagChange(event){
	this.placeholder = "";

	$(this).attr('size', $(this).val().length);
	split_tags = this.value.split(",");

	if(split_tags.length > 1){
		this.value = split_tags[split_tags.length - 1]
		for(i = 0; i < split_tags.length - 1; i++){
			addNewTag(this, split_tags[i])
		}
	}

	if(this.value.length > 32){
		this.value = this.value.substring(0, 32);
	}

	$(this).data("inputElement")[0].value =
		$(this).data("currentTags").join(",")
		+ (this.value.length > 0 ? "," + this.value : "");
}

$(document).ready(function(){
	$("#jack_tag").replaceWith(
		'<input class="hidden_input_field" id="jack_tag" name="jack_tag" type="hidden" value=""/><div class="fake_input_field"><input class="hidden_input_field" id="jack_tag_input" type="text" value="" placeholder="vore, vore, vore"/></div>');
	$("#jack_bro").replaceWith(
		'<input class="hidden_input_field" id="jack_bro" name="jack_bro" type="hidden" value=""/><div class="fake_input_field"><input class="hidden_input_field" id="jack_bro_input" type="text" value="" placeholder="user, user, user"/></div>');
	$("#jack_add_picture").hide()
	$("#jack_add_link").hide()
	$("#jack_add_bro").hide()
	$("#jack_add_tag").hide()

	$(".fake_input_field").bind("click", function(){
		$(this).find(".hidden_input_field").select();
	});

	$("#jack_tag_input").autocomplete({
		source: "/tag_suggestion/",
		select: function(event, ui){
			this.value = ui.item.value + ",";
			checkForTagChange.call(this, null);
			return false;
		},
		delay: 100,
		appendTo: "#jack_add_tag"
	})
	.bind("change paste keyup", checkForTagChange)
	.bind("keydown", checkForTagRemoval)
	.autoGrowInput({minWidth:30,comfortZone:30})
	.data({
		currentTags: [],
		inputElement: $("#jack_tag")
	});

	$("#jack_bro_input").autocomplete({
		source: "/bro_suggestion/",
		select: function(event, ui){
			this.value = ui.item.value + ",";
			checkForTagChange.call(this, null);
			return false;
		},
		delay: 100,
		appendTo: "#jack_add_bro"
	})
	.bind("change paste keyup", checkForTagChange)
	.bind("keydown", checkForTagRemoval)
	.autoGrowInput({minWidth:30,comfortZone:30})
	.data({
		currentTags: [],
		inputElement: $("#jack_bro")
	});
});

function addtime(){
	seconds++;
	if (seconds >= 60) {
		seconds = 0;
		minutes++;
		if (minutes >= 60) {
			minutes = 0;
			hours++;
			if (hours >= 24) {
				hours = 0;
				days++;
			}
		}
	}

	secondElement.innerHTML = (seconds > 9 ? seconds : "0" + seconds);
	minuteElement.innerHTML = (minutes > 9 ? minutes : "0" + minutes);
	if(hourElement != null){
		hourElement.innerHTML = (hours > 9 ? hours : "0" + hours);
		dayElement.innerHTML = days;
	}

	setTimeout(addtime, 1000);
}

function inittime(){
	secondElement = document.getElementById('jack_time_second');
	minuteElement = document.getElementById('jack_time_minute');
	hourElement = document.getElementById('jack_time_hour');
	dayElement = document.getElementById('jack_time_day');

	if(secondElement != null){
		seconds = parseInt(secondElement.innerHTML);
		minutes = parseInt(minuteElement.innerHTML);
		if(hourElement != null){
			hours = parseInt(hourElement.innerHTML);
			days = parseInt(dayElement.innerHTML);
		}
		addtime();
	}
}

window.addEventListener("load", inittime);

function add_punc(){
	if(!addedPunc){
		document.getElementById("new_jack_text").innerHTML += ',&nbsp;';
		addedPunc = true;

		jack_box = document.getElementById("new_jack_text");
		setEndOfContenteditable(jack_box);
	}
}

function textChange(){
	//var contenteditable = document.querySelector('[contenteditable]'),
	text = document.getElementById("new_jack_text").textContent;
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
	toggleAddLocation();
}

function toggleAddTag(){
	if(!addTag){
		document.getElementById("jack_add_tag").style.display = "block";
	}else{
		removeTag();
	}
	addTag = !addTag;
}

function removeTag(){
	addTag = true;
	document.getElementById("jack_add_tag").style.display = "none";
}

function toggleAddLocation(){
	geoEnabled = !geoEnabled
	if(geoEnabled){
		if (navigator.geolocation){
			navigator.geolocation.getCurrentPosition(showPosition);
		}else{
			document.getElementById("new_jack_text").textContent += "no geolocation";
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
		zoom: 8,
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
		{ visibility: 'on' }
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
		document.getElementById("image_source").value = "c";
		showImage(data_uri);
	});
}


function toggleAddImage(){
	if(!addPic){
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
	}else{
		removePicture();
	}
	addPic = !addPic;
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

function toggleAddLink(){
	if(!addLink){
		document.getElementById("jack_add_link").style.display = "block";
	}else{
		removeLink();
	}
	addLink = !addLink;
}
function removeLink(){
	document.getElementById("jack_add_link").style.display = "none";
}

function toggleAddBro(){
	if(!addBro){
		document.getElementById("jack_add_bro").style.display = "block";
	}else{
		removeBro();
	}
	addBro = !addBro;
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
			document.getElementById("image_source").value = "f";
		}

		reader.readAsDataURL(input.files[0]);
	}
}

function hideImage(){
	document.getElementById("add_pic").style.display = "block";
	document.getElementById("selected_image").style.display = "none";
	document.getElementById("jack_add_picture").setAttribute("class", "empty_box");
	document.getElementById("jack_add_picture").style.height = "6em";
	document.getElementById("jack_add_picture").style.margin = ".5em";
	document.getElementById("image_data").value = "";
	imageAdded = false;
}

function showImage(imageData){
	document.getElementById("image_data").value = imageData;
	document.getElementById("add_pic").style.display = "none";
	document.getElementById("selected_image").setAttribute("src", imageData);
	document.getElementById("selected_image").style.display = "block";
	document.getElementById("jack_add_picture").setAttribute("class", "jack_field");
	document.getElementById("jack_add_picture").style.height = "inherit";
	document.getElementById("jack_add_picture").style.margin = "0";
	imageAdded = true;
}
