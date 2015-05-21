// LocalServer

var normalStyle = null;
var user= null;
var localserver_addr = null;

function sendLoginRequest()
{

	
	 var success = validateLogin();

	if(success)
	{
		user = document.forms[0].username.value;
		var wait2 = document.getElementById("message");
		var form = document.getElementById("login-form");
		wait2.style.display = "block";
		form.style.display = "none";
		var xmlhttp=new XMLHttpRequest();

		 xmlhttp.open("GET","servlet_login?username="+document.forms[0].username.value+"&password="+document.forms[0].password.value,false);
 
		 xmlhttp.send();
 
		var result = (xmlhttp.responseText.split(",")[1]).split("}")[0];

		var response = xmlhttp.responseText;

		 if(result=='true')
		 {
			wait2.style.display = "none";
			var ok = document.getElementById("login_ok");
			ok.style.display = "block";
			var header = document.getElementById("login-intro");
			header.style.display = "none";
			var header2 = document.getElementById("afterlogin-intro");
			header2.style.display = "block";
			localserver_addr = (response.split(",")[2]).split("}")[0];
			console.log(localserver_addr);
		 }
		 else
		  {
		  	wait2.style.display = "none";
			form.style.display = "block";
		 	if(result=='false')
			{
				var errorBox =  document.getElementById("error-msg");
				errorBox.style.display = 'block';
				errorBox.innerHTML = "Login failed: username and/or password wrong.";
		 	}
			else
			{
		 		var errorBox =  document.getElementById("error-msg");
				errorBox.style.display = 'block';
				errorBox.innerHTML = "Error: you are already logged in the FROG network.";
		 	}
		 }
	}
}


/*								// Create the XHR object.
							function createCORSRequest(method, url) {
								
							  var xhr = new XMLHttpRequest();
							  
							  if ("withCredentials" in xhr) {
							    // XHR for Chrome/Firefox/Opera/Safari.
							    xhr.open(method, url, true);
							    xhr.send();	
								//location.reload();	
								
							  } else if (typeof XDomainRequest != "undefined") {
							    // XDomainRequest for IE.
							    xhr = new XDomainRequest();
							    xhr.open(method, url);		
							    xhr.send();
							    risultato = xhr.status;
								//location.reload();	
								
							  } else {
							    // CORS not supported.
							    xhr = null;
							  }
							  return xhr;
							}
							
							// Helper method to parse the title tag from the response.
							function getTitle(text) {
							  return text.match('<title>(.*)?</title>')[1];
							}
						
							// Make the actual CORS request.
							function makeCorsRequest() {
								// All HTML5 Rocks properties support CORS.
								var url = localserver_addr+"/servlet_logout?username="+user;
								var xhr = createCORSRequest('GET', url);
								
								if (xhr==null) {
							    alert('CORS not supported');
							    return;
								}
								
								xhr.onload = function() {
								    var text = xhr.responseText;
								    //var title = getTitle(text);
								    //alert('Response from CORS request to ' + text);
								    var result = (text.split(":")[1]).split("}")[0];
								    if(result=='true'){
										location.reload();
								    }
								    else alert('Logout failed');
								  };
								  
								xhr.onload();
							}
*/

function sendLogoutRequest(){
	
	var ok = document.getElementById("login_ok");
	ok.style.display = "none";
	
	var wait2 = document.getElementById("message");
	wait2.style.display = "block";
	
	var xmlhttp=new XMLHttpRequest();	
	
	//we have to contact with an absolute url, because after login we can't use the redirect page as our captive portal.
	//This leads to an error because we want to make a http Request to another domain.
	//For this reason, in the Logout servlet we set the Access-Control-Allow-Origin header to * (= any)
	//This allow the cross-domain http request
	xmlhttp.open("GET",localserver_addr+"/servlet_logout?username="+user,false);
	xmlhttp.send();
	var result = (xmlhttp.responseText.split(":")[1]).split("}")[0];

	if(result=='true'){
		location.reload();
	}
	 
}

function sendRegisterRequest()
{
	var success = validateRegistration();

	if(success)
	{
		//user = document.forms[0].username.value;
		var wait2 = document.getElementById("message");
		var form = document.getElementById("newuser-form");
		wait2.style.display = "block";
		form.style.display = "none";
		var xmlhttp=new XMLHttpRequest();

		 xmlhttp.open("GET","servlet_register?username="+document.forms[0].username.value+"&password="+document.forms[0].password.value+"&email="+document.forms[0].email.value,false);
		 var usern=document.forms[0].username.value;
		 user = usern;
		 var passn=document.forms[0].password.value;
		 xmlhttp.send();
 
		var result = (xmlhttp.responseText.split(":")[1]).split("}")[0];

		 if (result=='true')
		 {
			alert("New account created. You are now being logged in automatically in the FROG network.");
			xmlhttp.open("GET","servlet_login?username="+usern+"&password="+passn,false);
		 	xmlhttp.send();
		 	result = (xmlhttp.responseText.split(",")[1]).split("}")[0];
		 	var response = xmlhttp.responseText;
		 	console.log(result);
		 	if (result=='true')
		 	{
				wait2.style.display = "none";
				var ok = document.getElementById("login_ok");
				ok.style.display = "block";
				var header = document.getElementById("new-user");
				header.style.display = "none";
				var header2 = document.getElementById("afternew-user");
				header2.style.display = "block";
				localserver_addr = (response.split(",")[2]).split("}")[0];
				console.log(localserver_addr);
		 	}
		 	else{
		 		wait2.style.display = "none";
		 		form.style.display = "block";
		 		var errorBox =  document.getElementById("error-msg");
				errorBox.style.display = 'block';
				errorBox.innerHTML = "Login failed!";
		 	}
		 }
		 else
		 {
		 	wait2.style.display = "none";
			form.style.display = "block";
		 	if (result=='false')
			{
				var errorBox =  document.getElementById("error-msg");
				errorBox.style.display = 'block';
				errorBox.innerHTML = "Error: cannot create the new account as the provided username already exists.";
		 	}
			else
			{
		 		var errorBox =  document.getElementById("error-msg");
				errorBox.style.display = 'block';
				errorBox.innerHTML = "Error: you are already logged in the FROG network.";
		 	}
		 }
	}
}


function validateLogin()
{
	// reset parameters
	var errorBox =  document.getElementById("error-msg");
	errorBox.style.display = 'none';
	document.forms[0].username.style.border = normalStyle;
	document.forms[0].password.style.border = normalStyle;

	var username = document.forms[0].username.value;
	if(username.length == 0)
	{ 
		normalStyle = document.forms[0].username.style.border;
		document.forms[0].username.style.border = "1px solid #ff876f";
		document.forms[0].username.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: missing username."
		return false;
	}

	var psw = document.forms[0].password.value;
	if(psw.length == 0)
	{ 
		normalStyle = document.forms[0].password.style.border;
		document.forms[0].password.style.border = "1px solid #ff876f";
		document.forms[0].password.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: missing password."
		return false;
	}

	return true;
}


function validateRegistration()
{
	// reset parameters
	var emailRegEx = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
	var errorBox =  document.getElementById("error-msg");
	errorBox.style.display = 'none';
	document.forms[0].username.style.border = normalStyle;
	document.forms[0].password.style.border = normalStyle;
	document.forms[0].pwdcfrm.style.border = normalStyle;
	document.forms[0].email.style.border = normalStyle;

	var username = document.forms[0].username.value;
	if(username.length == 0)
	{ 
		normalStyle = document.forms[0].username.style.border;
		document.forms[0].username.style.border = "1px solid #ff876f";
		document.forms[0].username.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: missing username."
		return false;
	}

	var psw = document.forms[0].password.value;
	if(psw.length == 0)
	{ 
		normalStyle = document.forms[0].password.style.border;
		document.forms[0].password.style.border = "1px solid #ff876f";
		document.forms[0].password.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: missing password."
		return false;
	}

	var psw2 = document.forms[0].pwdcfrm.value;
	if(psw2.length == 0)
	{ 
		normalStyle = document.forms[0].pwdcfrm.style.border;
		document.forms[0].pwdcfrm.style.border = "1px solid #ff876f";
		document.forms[0].pwdcfrm.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: missing confirmation password."
		return false;
	}

	var email = document.forms[0].email.value;
	if(email.length == 0)
	{ 
		normalStyle = document.forms[0].email.style.border;
		document.forms[0].email.style.border = "1px solid #ff876f";
		document.forms[0].email.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: missing email address."
		return false;
}

	if(psw!=psw2)
	{
		normalStyle = document.forms[0].password.style.border;
		document.forms[0].password.style.border = "1px solid #ff876f";
		document.forms[0].password.style.border = "1px solid #ff876f";
		document.forms[0].password.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: password does not match the data you entered in the confirmation password box."
		return false;
	}

	if(!emailRegEx.test(email))
	{
		normalStyle = document.forms[0].email.style.border;
		document.forms[0].email.style.border = "1px solid #ff876f";
		document.forms[0].email.focus();

		errorBox.style.display = 'block';
		errorBox.innerHTML = "Error: invalid email address."
		return false;
	}

	return true;
}


function submitonenter(formid,evt,thisObj) {
	evt = (evt) ? evt : ((window.event) ? window.event : "")
	if (evt)
	{
		if ( evt.keyCode==13 || evt.which==13 )
		{
			document.getElementById(formid).click();
		}
	}
}