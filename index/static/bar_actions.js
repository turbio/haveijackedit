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

	$("#bar_search").autocomplete({
		source: "/search_suggestion/",
		response: function(event, ui){
			results = ui['content'];
			for(i in results){
				if(ui['content'][i]['type'] == 'tag'){
					ui['content'][i]['label'] = '<i class="material-icons">label</i> ';
				}else if(ui['content'][i]['type'] == 'user'){
					ui['content'][i]['label'] = '<i class="material-icons">person</i> ';
				}else{
					ui['content'][i]['label'] = '';
				}

				ui['content'][i]['label'] += ui['content'][i]['text'];

				ui['content'][i]['value'] =
					ui['content'][i]['type'] + ":" + ui['content'][i]['text'].replace(' ', '+');
			}
		},
		delay: 300,
		html: true
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
