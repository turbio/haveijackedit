var addedPunc = false;

function add_punc(){
	if(!addedPunc){
		document.getElementById("new_jack_box").innerHTML += ', ';
		addedPunc = true;
	}
}
