// LocalServer

var normalStyle = null;
var user= null;
var timeout = 4 * 60 * 1000 ;
var instantiate_timeout = 15 * 1000;
var delete_timeout = 10 * 1000;
var updatePercentageTime = 3000;
var token = null;
var req_instantiate_status;
var progressTimer;

var form; 
var loading;

function disinstantiateProfile(user, pwd)
{
	form = document.getElementById("newuser-form");
	loading = document.getElementById("loading");

	loading.style.display = "block";
	token = getTokenFromKeystone(keystone_ip, keystone_port, user, pwd);
	sendDeleteToGlobalOrch(orchestrator_ip, orchestrator_port, token, proxy_addr);
}

function instantiateProfile(user, pwd)
{
	form = document.getElementById("newuser-form");
	loading = document.getElementById("loading");

	loading.style.display = "block";
	token = getTokenFromKeystone(keystone_ip, keystone_port, user, pwd);
	sendPutToGlobalOrch(orchestrator_ip, orchestrator_port, token, proxy_addr);

}

function getTokenFromKeystone(addr, port, user, pwd)
{
	var method = "POST";	
	var xmlhttp = new XMLHttpRequest();
	var body = '{"auth": {"tenantName": "'+user+'", "passwordCredentials": {"username": "'+user+'", "password": "'+pwd+'"}}}'
	var header1 = "Content-Type: application/json"
	var header2 = "Accept: application/json"
	var remove_url = "http://"+proxy_addr+path+"/proxy.php?headers=false&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+addr+":"+port+"/v2.0/tokens&data="+body;


	xmlhttp.open("POST",remove_url,false);
 
	xmlhttp.send();
	var response = xmlhttp.responseText;
	console.log(response);
	var obj = JSON.parse(response);
	token = obj.access.token.id;
	return token;

}


function sendPutToGlobalOrch(addr, port, token, proxy_addr)
{
	var method = "PUT";
	
	token = encodeURIComponent(token)
	var header = "X-Auth-Token: "+token
	var header1 = "Content-Type: application/json"
	var header2 = "Accept: application/json"
	var body = '{"session":{"session_param" : {}}}'
		
    var remove_url = "http://"+proxy_addr+path+"/proxy.php?headers=true&header_send[]="+header+"&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+addr+":"+port+"/orchestrator&data="+body;
	
	req = new XMLHttpRequest();
	req.open("POST",remove_url, true);
	req.onreadystatechange = orchestratorInstantiationResponse;
	req.send(null);

}

function sendDeleteToGlobalOrch(addr, port, token, proxy_addr)
{
	var method = "DELETE";
	
	token = encodeURIComponent(token)
	var header = "X-Auth-Token: "+token
	var header1 = "Content-Type: application/json"
	var header2 = "Accept: application/json"
	var body = '{"session":{"session_param" : {}}}'
    var remove_url = "http://"+proxy_addr+path+"/proxy.php?headers=true&header_send[]="+header+"&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+addr+":"+port+"/orchestrator&data="+body;
	
	req = new XMLHttpRequest();
	req.open("POST",remove_url, true);
	req.onreadystatechange = orchestratorDeleteResponse;
	req.send(null);
	
	//xmlHttpTimeout = setTimeout(ajaxTimeout, timeout); 
}

function ajaxTimeout(){
    console.log("Request aborted");
	req.abort();
	window.clearInterval(xmlHttpTimeout);
}

function orchestratorDeleteResponse(){
	/*
	 * Wait until the graph is completed
	 */
	if (req.readyState == 4) {
		token = encodeURIComponent(token)
		var header = "X-Auth-Token: "+token
		console.log("X-Auth-Token: "+token)
		var header1 = "Content-Type: application/json"
		var header2 = "Accept: application/json"
		method = "GET"
		console.log("Delete status"+req.status);
		remote_url = "http://"+proxy_addr+path+"/proxy.php?headers=true&header_send[]="+header+"&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+orchestrator_ip+":"+orchestrator_port+"/orchestrator";
		
		// DEVE ESSERE RIPETUTO OGNI 3000 millisecondi
		req_delete_status = new XMLHttpRequest();
		req_delete_status.open("POST",remote_url, true);
		req_delete_status.onreadystatechange = orchestratorStatusDeleteResponse;
		req_delete_status.send(null);
		progressTimer = window.setInterval(function(){
			    req_delete_status = new XMLHttpRequest();
				req_delete_status.open("POST",remote_url, true);
				req_delete_status.onreadystatechange = orchestratorStatusDeleteResponse;
				req_delete_status.send(null);
		}, 3000);
		// Abort timeout, if we cycle forever waiting for the graph to be deinstatiated
		xmlHttpTimeout = setTimeout(function() {
			console.log("Timeout ended");
	
			window.clearInterval(progressTimer);
			req_delete_status.abort();
		}, timeout); 
	}		
}

function orchestratorInstantiationResponse(){
	/*
	 * Wait until the graph is completed
	 */
	if (req.readyState == 4) {
		token = encodeURIComponent(token)
		var header = "X-Auth-Token: "+token
		console.log("X-Auth-Token: "+token)
		var header1 = "Content-Type: application/json"
		var header2 = "Accept: application/json"
		method = "GET"
		console.log("Instantiated status"+req.status);
		remote_url = "http://"+proxy_addr+path+"/proxy.php?headers=true&header_send[]="+header+"&header_send[]="+header1+"&header_send[]="+header2+"&method="+method+"&url=http://"+orchestrator_ip+":"+orchestrator_port+"/orchestrator";
		
		// DEVE ESSERE RIPETUTO OGNI 5000 millisecondi
		req_instantiate_status = new XMLHttpRequest();
		req_instantiate_status.open("POST",remote_url, true);
		req_instantiate_status.onreadystatechange = orchestratorStatusInstantiationResponse;
		req_instantiate_status.send(null);
		progressTimer = window.setInterval(function(){
			    req_instantiate_status = new XMLHttpRequest();
				req_instantiate_status.open("POST",remote_url, true);
				req_instantiate_status.onreadystatechange = orchestratorStatusInstantiationResponse;
				req_instantiate_status.send(null);
		}, 5000);
		// Abort timeout, if we cycle forever waiting for the graph to be completely instantiated
		xmlHttpTimeout = setTimeout(function() {
			console.log("Timeout ended");
	
			window.clearInterval(progressTimer);
			req_instantiate_status.abort();
		}, timeout); 
	}
	
}

function orchestratorStatusDeleteResponse(){
	console.log("orchestratorStatusDeleteResponse readyState: "+req_delete_status.readyState);
	if (req_delete_status.readyState == 4) {
		console.log("Status status: "+req_delete_status.status);
		if(req_delete_status.status == 404){
			window.clearInterval(progressTimer);
			xmlHttpTimeout = setTimeout(function() {
				console.log("Messages timeout ended");
				loading.style.display = "none";
				var disinstantiated = document.getElementById("disinstantiated");
				disinstantiated.style.display = "block";
				var login_graph = document.getElementById("login-form");
				login_graph.style.display = "none";
				console.log("orchestrator returns");
			}, delete_timeout); 
		}
	}
}

function orchestratorStatusInstantiationResponse(){
	console.log("orchestratorStatusDeleteResponse readyState: "+req_instantiate_status.readyState);
	if (req_instantiate_status.readyState == 4) {
		console.log("Status status: "+req_instantiate_status.status);
		if(req_instantiate_status.status == 201){
			window.clearInterval(progressTimer);
			xmlHttpTimeout = setTimeout(function() {
				console.log("Messages timeout ended");
				loading.style.display = "none";
				var ok = document.getElementById("login_ok");
				ok.style.display = "block";
				var login_graph = document.getElementById("login-form");
				login_graph.style.display = "none";
				console.log("orchestrator returns");
			}, instantiate_timeout); 
		}
	}
}

