function post(path, params, callback){
	params = "csrfmiddlewaretoken=" + getCookie('csrftoken') + "&" + params;
	http = new XMLHttpRequest();
	http.open("POST", path, true);

	//Send the proper header information along with the request
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	http.setRequestHeader("Content-length", params.length);
	http.setRequestHeader("Connection", "close");

	http.onreadystatechange = callback
	http.send(params);
}

function downvote(postid){
	vote_down = document.getElementById("vote_down_" + postid);
	vote_up = document.getElementById("vote_up_" + postid);

	if(vote_down.className == "vote_button"){
		post("/vote/", "jack=" + postid + "&choice=d", updateVotes);
		vote_down.className = "vote_button_selected";
		vote_up.className = "vote_button";
	}else{
		post("/vote/", "jack=" + postid + "&choice=n", updateVotes);
		vote_down.className = "vote_button";
		vote_up.className = "vote_button";
	}
}

function upvote(postid){
	vote_up = document.getElementById("vote_up_" + postid);
	vote_down = document.getElementById("vote_down_" + postid);

	if(vote_up.className == "vote_button"){
		post("/vote/", "jack=" + postid + "&choice=u", updateVotes);
		vote_up.className = "vote_button_selected";
		vote_down.className = "vote_button";
	}else{
		post("/vote/", "jack=" + postid + "&choice=n", updateVotes);
		vote_up.className = "vote_button";
		vote_down.className = "vote_button";
	}
}

function updateVotes(){
	console.log(http.responseText)
	//alert(http.responseText);
	//document.getElementById("wrapper").innerHTML = http.responseText
}

function getCookie(name){
	var cookieValue = null;
	if (document.cookie && document.cookie != ''){
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
