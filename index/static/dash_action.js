var addedPunc = false;

function add_punc(){
	if(!addedPunc){
		document.getElementById("new_jack_box").innerHTML += ', ';
		addedPunc = true;
	}
}

function textChange(){
	jackChars = document.getElementById("new_jack_box").innerHTML;
	usedChars = jackChars.length;
	document.getElementById("remaining_chars").innerHTML = (usedChars + '/160');
}
