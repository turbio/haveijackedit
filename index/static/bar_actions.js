var showCommunityBar = false;

$(document).ready(function(){
	$("#drop_down_link").bind("click", function(e){
		if(e){
			e.stopPropagation();
		}else{
			window.event.cancelBubble = true;
		}
		document.getElementById("user_actions").style.display = "flex";
		document.getElementById("actions_icon").className = "titlebar_button  btn_right titlebar_button_selected";
		e.preventDefault();
	});

	$("#sort_button").bind("click", function(e){
		if(showCommunityBar){
			document.getElementById("community_bar").style.top = "-1.5em";
		}else{
			document.getElementById("community_bar").style.top = "1.5em";
		}
		showCommunityBar = !showCommunityBar;
		e.preventDefault();
	});
});

document.onclick = function(){
	document.getElementById("user_actions").style.display = "none";

	document.getElementById("actions_icon").className = "titlebar_button  btn_right";
}
