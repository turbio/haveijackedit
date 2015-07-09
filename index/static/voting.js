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
	post("/vote/", "jack=" + postid + "&choice=u", cb)
}

function upvote(postid){
	post("/vote/", "jack=" + postid + "&choice=d", cb)
}

function cb(){
	if(http.readyState == 4 && http.status == 200) {
		//alert(http.responseText);
	}
}

function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
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
