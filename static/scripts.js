function onLinkedInLoad() {
     IN.Event.on(IN, "auth", onLinkedInAuth);
     document.getElementById("working").innerHTML="";
}

function onLinkedInAuth() {
	 document.getElementById("working").innerHTML="getting your details...";
     IN.API.Profile("me")
     .fields("firstName,lastName,pictureUrl,id")//"skills") //add sklls later
     .result(checkDetails);//do this function once the profile information has been requested/received    
}

function checkDetails(profiles) {
	//member = profiles.values[0];
	console.log('now we will redirect to checkuser');
	document.getElementById("user_details_form").submit();	
}


// logout function
function onLinkedInLogoutClick(){
	console.log("log out button clicked")
	window.location.href='/logout'
}

//test function
function logout(){
	console.log("user will be logged out")
	IN.User.logout();
	IN.Event.on(IN, "logout", onLinkedInLogout)
	
}

// callback function to redirect to user to the homepage after logout.	
function onLinkedInLogout(){
	// User is logged out
	console.log("user has been logged out of LinkedIn");
	document.getElementById("redirecting").innerHTML="redirecting to welcome page"
	window.location.href='/';
}

function focusDiv(divid){
	document.getElementById("fadescreen").style.visibility="visible"
	document.getElementById(divid).style.zIndex="2"
}

function enableTextEdit(textelementid){
	document.getElementById(textelementid).removeAttribute("disabled")
}

function enableObjectiveEdit(id){
	document.getElementById(id+"_due_date").removeAttribute("disabled")
	document.getElementById(id+"_status").removeAttribute("disabled")
	document.getElementById(id+"_traffic_light").removeAttribute("disabled")
	document.getElementById(id+"_description").removeAttribute("disabled")
}

function objErrorMessage(id){
	console.log(id)
	document.getElementById(id).innerHTML="Please check that you have entered a title, valid due date and description."
}

function enableEvidenceEdit(id){
	document.getElementById(id+"_details").removeAttribute("disabled")
}

function showElement(elementid){
	document.getElementById(elementid).style.display="block"
}

function unhideElement(elementid){
	document.getElementById(elementid).style.visibility="visible"
}

function hideElement(elementid){
	document.getElementById(elementid).style.visibility="hidden"
}

// function displayoption(value){
	// document.getElementById("display_by_objectives").style.display="none"
	// document.getElementById("display_by_competencies").style.display="none"
	// document.getElementById("display_by_"+value).style.display="block"
	// document.getElementById("test").innerHTML="{% include 'includes/objective.html' %}"
// }

function showHelp(){
	document.getElementById("help_bar").setAttribute("class","help_bar_open")
	document.getElementById("help_tag").setAttribute("onclick","hideHelp()")
	document.getElementById("help_tag").setAttribute("onmouseout","")
	document.getElementById("help_tag").style.backgroundColor="#f6f6f6"
	document.getElementById("help_tag").innerHTML="-?"
	document.getElementById("help_container").style.display="block"
	
}

function hideHelp(){
	document.getElementById("help_bar").setAttribute("class","help_bar_closed")
	document.getElementById("help_tag").setAttribute("onclick","showHelp()")
	document.getElementById("help_tag").setAttribute("onmouseout","lowlightHelp()")
	document.getElementById("help_tag").style.backgroundColor="white"
	document.getElementById("help_tag").innerHTML="+?"
	document.getElementById("help_container").style.display="none"
}

function highlightHelp(){
	document.getElementById("help_bar").style.boxShadow="0px 2px 2px #888888"
	document.getElementById("help_tag").style.boxShadow="1px 2px 2px #888888"
}

function lowlightHelp(){
	document.getElementById("help_bar").style.boxShadow=""
	document.getElementById("help_tag").style.boxShadow=""
}

function helpTagMarginLeft(x){
	document.getElementById("help_tag").style.marginLeft=x+"px"
}

function helpTagMarginRight(x){
	document.getElementById("help_tag").style.right=x+"px"
}
