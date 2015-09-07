var showSortBar = false;
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
		if(showSortBar){
			document.getElementById("sort_bar").style.top = "-1.5em";
		}else{
			document.getElementById("sort_bar").style.top = "1.5em";
			document.getElementById("community_bar").style.top = "-1.5em";
			showCommunityBar = false;
		}
		showSortBar = !showSortBar;
		e.preventDefault();
	});

	$("#community_button_link").bind("click", function(e){
		if(showCommunityBar){
			document.getElementById("community_bar").style.top = "-1.5em";
		}else{
			document.getElementById("community_bar").style.top = "1.5em";
			document.getElementById("sort_bar").style.top = "-1.5em";
			showSortBar = false;
		}
		showCommunityBar = !showCommunityBar;
		e.preventDefault();
	});
});

document.onclick = function(){
	document.getElementById("user_actions").style.display = "none";

	document.getElementById("actions_icon").className = "titlebar_button  btn_right";
}
