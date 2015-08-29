window.addEventListener("load", function() {
	asignClick()
});

function asignClick(){
	document.getElementById('drop_down_link').onclick = function(e){
		if(e){
			e.stopPropagation();
		}else{
			window.event.cancelBubble = true;
		}
		document.getElementById("user_actions").style.display = "flex";
		document.getElementById("actions_icon").className = "titlebar_button  btn_right titlebar_button_selected";
	}
}

document.onclick = function(){
	document.getElementById("user_actions").style.display = "none";

	document.getElementById("actions_icon").className = "titlebar_button  btn_right";
}
