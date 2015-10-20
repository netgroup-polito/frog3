// LocalServer

var normalStyle = null;
var user= null;
var localserver_addr = null;
var timeout = 5000;

// POLITO
var keystone_ip = "130.192.225.236";
var keystone_port = "35357";
var orchestrator_ip = "130.192.225.248";
var orchestrator_port = "8000";

// CISCO
//var keystone_ip = "192.168.1.3";
//var keystone_port = "35357";
//var orchestrator_ip = "192.168.1.5";
//var orchestrator_port = "8000";


function disinstantiateProfile(user, pwd)
{
	var token = null;
	var wait2 = document.getElementById("message");
	var form = document.getElementById("newuser-form");
	
	wait2.style.display = "none";
	var ok = document.getElementById("disinstantiated");
	ok.style.display = "block";
	console.log(localserver_addr);
	var login_graph = document.getElementById("login-form");
	login_graph.style.display = "none";
	
	token = getTokenFromKeystone(keystone_ip, keystone_port, user, pwd);
	sendDeleteToGlobalOrch(orchestrator_ip, orchestrator_port, token, keystone_ip);
}

function instantiateProfile(user, pwd)
{

	var token = null;
	var wait2 = document.getElementById("message");
	var form = document.getElementById("newuser-form");
	
		
	wait2.style.display = "none";
	var ok = document.getElementById("login_ok");
	ok.style.display = "block";
	console.log(localserver_addr);
	var login_graph = document.getElementById("login-form");
	login_graph.style.display = "none";
		
	token = getTokenFromKeystone(keystone_ip, keystone_port, user, pwd);
	sendPutToGlobalOrch(orchestrator_ip, orchestrator_port, token, keystone_ip);

}

function getTokenFromKeystone(addr, port, user, pwd)
{
	var method = "POST";
	var token = null;
	
	//user = document.forms[0].username.value;
	//pwd = document.forms[0].password.value;
	
	var xmlhttp = new XMLHttpRequest();
	var body = '{"auth": {"tenantName": "'+user+'", "passwordCredentials": {"username": "'+user+'", "password": "'+pwd+'"}}}'
	var header1 = "Content-Type: application/json"
	var header2 = "Accept: application/json"
	var remove_url = "http://"+addr+"/instantiate/proxy.php?headers=false&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+addr+":"+port+"/v2.0/tokens&data="+body;


	xmlhttp.open("POST",remove_url,false);
 
	xmlhttp.send();
	var response = xmlhttp.responseText;
	console.log(response);
	var obj = JSON.parse(response);
	token = obj.access.token.id;
	return token;

}


function sendPutToGlobalOrch(addr, port, token, keystone_ip)
{
	var method = "PUT";
	
	token = encodeURIComponent(token)
	var header = "X-Auth-Token: "+token
	var header1 = "Content-Type: application/json"
	var header2 = "Accept: application/json"
	var body = '{"session":{"session_param" : { "test":"test"}}}'
		
    var remove_url = "http://"+keystone_ip+"/instantiate/proxy.php?headers=true&header_send[]="+header+"&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+addr+":"+port+"/orchestrator&data="+body;
	
	req = new XMLHttpRequest();
	req.open("POST",remove_url, true);
	req.onreadystatechange = callback;
	req.send(null);
	
	xmlHttpTimeout = setTimeout(ajaxTimeout, timeout); 
}

function sendDeleteToGlobalOrch(addr, port, token, keystone_ip)
{
	var method = "DELETE";
	
	token = encodeURIComponent(token)
	var header = "X-Auth-Token: "+token
	var header1 = "Content-Type: application/json"
	var header2 = "Accept: application/json"
	var body = '{"session":{"session_param" : { "test":"test"}}}'
    var remove_url = "http://"+keystone_ip+"/instantiate/proxy.php?headers=true&header_send[]="+header+"&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+addr+":"+port+"/orchestrator&data="+body;
	
	req = new XMLHttpRequest();
	req.open("POST",remove_url, true);
	req.onreadystatechange = callback;
	req.send(null);
	
	xmlHttpTimeout = setTimeout(ajaxTimeout, timeout); 
}

function ajaxTimeout(){
    console.log("Request aborted");
	req.abort();
	window.clearInterval(xmlHttpTimeout);
}

function callback(){
	console.log("Callback");
}

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

		 xmlhttp.open("GET","Login?username="+document.forms[0].username.value+"&password="+document.forms[0].password.value,false);
 
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
//			var header2 = document.getElementById("afterlogin-intro");
//			header2.style.display = "block";
//			localserver_addr = (response.split(",")[2]).split("}")[0];
			var uri  = (response.split(",")[2]).split("}")[0];
			window.location.replace(uri);
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

