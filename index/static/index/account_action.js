function show_signup(){
	document.getElementById("signup").style.display = "block";
	document.getElementById("signin").style.display = "none";
}

function show_signin(){
	document.getElementById("signin").style.display = "block";
	document.getElementById("signup").style.display = "none";
}

function hide_dialog(){
	document.getElementById("signin").style.display = "none";
	document.getElementById("signup").style.display = "none";
}

function username_entered(){
	var username = document.getElementById("signup_username").value;

	if(username == ""){
		document.getElementById("signup_username").style["border-color"] = "#ff0000";
		document.getElementById("signup_error").style["display"] = "block";
		document.getElementById("signup_error").innerHTML = "you must enter a username";
		return;
	}

	var alphanumericExp = /^[a-z0-9]+$/i;
	if(!username.match(alphanumericExp)){
		document.getElementById("signup_username").style["border-color"] = "#ff0000";
		document.getElementById("signup_error").style["display"] = "block";
		document.getElementById("signup_error").innerHTML = "username must be alphanumeric";
	}else{
		document.getElementById("signup_username").style["border-color"] = "#888";
		document.getElementById("signup_error").style["display"] = "none";
	}
}
