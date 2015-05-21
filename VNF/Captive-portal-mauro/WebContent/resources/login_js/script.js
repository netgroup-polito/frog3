// LocalServer
var normalStyle = null;
var user = null;
var localserver_addr = null;

function sendLoginRequest() {


    var success = validateLogin();

    if (success) {
        user = document.forms[0].username.value;
        var wait2 = document.getElementById("message");
        var form = document.getElementById("login-form");
        wait2.style.display = "block";
        form.style.display = "none";
        var xmlhttp = new XMLHttpRequest();

        xmlhttp.open("GET", "Login?username=" + document.forms[0].username.value + "&password=" + document.forms[0].password.value, false);
        xmlhttp.send();
        console.log('minchia succede');
        //"{\"status\":\"error\", \"accountable\": \"orchestrator\"}"
        var response = JSON.parse(xmlhttp.responseText);
        console.log('minchia succede 2');
        var status = response['status'];
        var accountable = response['accountable'];
        //\"reason\": \"authentication\"
        var reason = response['reason'];
        
        //out.print("{\"status\":\"success\"}");

        if (status == 'success') {
        	console.log('success');
            wait2.style.display = "none";
            var ok = document.getElementById("login_ok");
            ok.style.display = "block";
            var header = document.getElementById("login-intro");
            header.style.display = "none";
            var uri = response['uri'];
            console.log(uri);
            window.location.replace(uri); 
        } else {
            wait2.style.display = "none";
            form.style.display = "block";
            if (accountable == 'keystone' && reason == 'authentication') {
                var errorBox = document.getElementById("error-msg");
                errorBox.style.display = 'block';
                errorBox.innerHTML = "Login failed: username and/or password wrong.";
            } else if(accountable == 'keystone'){
            	var errorBox = document.getElementById("error-msg");
                errorBox.style.display = 'block';
                errorBox.innerHTML = "Error: some problems occurr with the authentication server";
            } else if(accountable == 'controller openflow'){
            	var errorBox = document.getElementById("error-msg");
                errorBox.style.display = 'block';
                console.log("[01] Error: some problems occurr with the SDN controller");
                errorBox.innerHTML = "Error: internal error [code: 01].";
            } else if(accountable == 'orchestrator'){
            	var errorBox = document.getElementById("error-msg");
                errorBox.style.display = 'block';
                console.log("[02] Error: some problems occurr with the orchestrator");
                errorBox.innerHTML = "Error: internal error [code: 02].";
            } else {
                var errorBox = document.getElementById("error-msg");
                errorBox.style.display = 'block';
                errorBox.innerHTML = "Error: internal error [code: 03].";
            }
        }
    }
}

function validateLogin() {
    // reset parameters
    var errorBox = document.getElementById("error-msg");
    errorBox.style.display = 'none';
    document.forms[0].username.style.border = normalStyle;
    document.forms[0].password.style.border = normalStyle;

    var username = document.forms[0].username.value;
    if (username.length == 0) {
        normalStyle = document.forms[0].username.style.border;
        document.forms[0].username.style.border = "1px solid #ff876f";
        document.forms[0].username.focus();

        errorBox.style.display = 'block';
        errorBox.innerHTML = "Error: missing username.";
        return false;
    }

    var psw = document.forms[0].password.value;
    if (psw.length == 0) {
        normalStyle = document.forms[0].password.style.border;
        document.forms[0].password.style.border = "1px solid #ff876f";
        document.forms[0].password.focus();

        errorBox.style.display = 'block';
        errorBox.innerHTML = "Error: missing password.";
        return false;
    }

    return true;
}

function submitonenter(formid,evt,thisObj) {
	evt = (evt) ? evt : ((window.event) ? window.event : "");
	if (evt)
	{
		if ( evt.keyCode==13 || evt.which==13 )
		{
			document.getElementById(formid).click();
		}
	}
}