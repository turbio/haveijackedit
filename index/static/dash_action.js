var addedPunc = false;

function add_punc(){
	if(!addedPunc){
		document.getElementById("new_jack_box").innerHTML += ',&nbsp;';
		addedPunc = true;

		jack_box = document.getElementById("new_jack_box");
		setEndOfContenteditable(jack_box);
	}
}

function textChange(){
	//var contenteditable = document.querySelector('[contenteditable]'),
	text = document.getElementById("new_jack_box").textContent;
	document.getElementById("new_jack_post_box").value = text;
	usedChars = text.length;
	document.getElementById("remaining_chars").innerHTML = (usedChars + '/160');
}

function setEndOfContenteditable(contentEditableElement){
	var range,selection;
	if(document.createRange){ //Firefox, Chrome, Opera, Safari, IE 9+
		range = document.createRange();//Create a range (a range is a like the selection but invisible)
		range.selectNodeContents(contentEditableElement);//Select the entire contents of the element with the range
		range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
		selection = window.getSelection();//get the selection object (allows you to change selection)
		selection.removeAllRanges();//remove any selections already made
		selection.addRange(range);//make the range you have just created the visible selection
	}
	else if(document.selection){ //IE 8 and lower
		range = document.body.createTextRange();//Create a range (a range is a like the selection but invisible)
		range.moveToElementText(contentEditableElement);//Select the entire contents of the element with the range
		range.collapse(false);//collapse the range to the end point. false means collapse to end rather than the start
		range.select();//Select the range (make it the visible selection
	}
}