function post(path, params, callback){
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
	post("/downvote/", "post=" + postid, cb)
}

function upvote(postid){
	post("/upvote/", "post=" + postid, cb)
}

function cb(){
	if(http.readyState == 4 && http.status == 200) {
		alert(http.responseText);
	}
}
