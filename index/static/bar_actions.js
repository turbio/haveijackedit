function show_user_actions(e){
	if(e){
		e.stopPropagation();
	}else{
		window.event.cancelBubble = true;
	}
	document.getElementById("user_actions").style.display = "block";
	document.getElementById("actions_icon").style.backgroundColor = "white";
	document.getElementById("actions_icon").style.color = "black";
}

//document.getElementById('user_actions').onclick = function(e){
	//if(e){
		//e.stopPropagation();
	//}else{
		//window.event.cancelBubble = true;
	//}
//}

document.onclick = function(){
	document.getElementById("user_actions").style.display = "none";
}
