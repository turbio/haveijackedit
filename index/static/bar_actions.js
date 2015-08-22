function show_user_actions(e){
	if(e){
		e.stopPropagation();
	}else{
		window.event.cancelBubble = true;
	}
	document.getElementById("user_actions").style.display = "flex";
	document.getElementById("actions_icon").className = "titlebar_button  btn_right titlebar_button_selected";
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

	document.getElementById("actions_icon").className = "titlebar_button  btn_right";
}
