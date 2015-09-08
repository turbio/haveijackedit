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
		$("#sort_bar").toggleClass("sub_bar_visible");
		$("#sort_button").toggleClass("titlebar_button_selected_secondary");

		$("#community_bar").removeClass("sub_bar_visible");
		$("#community_button_icon").removeClass("titlebar_button_selected_secondary");
		e.preventDefault();
	});

	$("#community_button_link").bind("click", function(e){
		$("#community_bar").toggleClass("sub_bar_visible");
		$("#community_button_icon").toggleClass("titlebar_button_selected_secondary");

		$("#sort_bar").removeClass("sub_bar_visible");
		$("#sort_button").removeClass("titlebar_button_selected_secondary");

		e.preventDefault();
	});
});

document.onclick = function(){
	document.getElementById("user_actions").style.display = "none";

	document.getElementById("actions_icon").className = "titlebar_button  btn_right";
}
