// LocalServer

var normalStyle = null;
var user= null;
var localserver_addr = null;
var timeout = 5000;


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
	sendDeleteToGlobalOrch(orchestrator_ip, orchestrator_port, token, proxy_addr);
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
	sendPutToGlobalOrch(orchestrator_ip, orchestrator_port, token, proxy_addr);

}

function getTokenFromKeystone(addr, port, user, pwd)
{
	var method = "POST";
	var token = null;
	
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
	req.onreadystatechange = orchestratorResponse;
	req.send(null);
	
	xmlHttpTimeout = setTimeout(ajaxTimeout, timeout); 
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
	req.onreadystatechange = orchestratorResponse;
	req.send(null);
	
	xmlHttpTimeout = setTimeout(ajaxTimeout, timeout); 
}

function ajaxTimeout(){
    console.log("Request aborted");
	req.abort();
	window.clearInterval(xmlHttpTimeout);
}

function orchestratorResponse(){
	console.log("orchestrator returns");
}


