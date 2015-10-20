<?php
//sleep(10);

// Get the url of to be proxied
// Is it a POST or a GET?
$url = (isset($_POST['url'])) ? $_POST['url'] : $_GET['url'];
$headers = (isset($_POST['headers'])) ? $_POST['headers'] : $_GET['headers'];
$mimeType =(isset($_POST['mimeType'])) ? $_POST['mimeType'] : $_GET['mimeType'];
$method = (isset($_POST['method'])) ? $_POST['method'] : $_GET['method'];
$header_send = (isset($_POST['header_send'])) ? $_POST['header_send'] : $_GET['header_send'];



//Start the Curl session
$session = curl_init($url);
// If it's a POST, put the POST data in the body
if (isset($_POST['method']) or isset($_GET['method'])) {
	$postvars = '';
	$postvars .=$_GET['data'];
	
	//while ($element = current($_POST)) {
	//	$postvars .= key($_POST).'='.$element.'&';
	//	next($_POST);
	//}
	
	//echo $postvars."\n";
	$postvars = stripslashes($postvars);
	//echo $postvars."\n";

	//curl_setopt($session, CURLOPT_HTTPHEADER, array("Content-Type: application/json", "Accept: application/json"));

	curl_setopt ($session, CURLOPT_POST, 1);
	curl_setopt ($session, CURLOPT_POSTFIELDS, $postvars);
	//curl_setopt($session, CURLOPT_RETURNTRANSFER, 1);
    //curl_setopt($session, CURLOPT_VERBOSE, 1);
	curl_setopt($session, CURLOPT_HEADER, 1);
}

// Prepare header
//addslashes(htmlspecialchars(
for ($i = 0, $n = count($header_send) ; $i < $n ; $i++)
{
    $header_send[$i] = addslashes(htmlspecialchars($header_send[$i]));
    if(strcmp($method,"DELETE") == 0){
    	echo "bellazio";
    	echo $header_send[$i];
    }
     
}
curl_setopt($session, CURLOPT_HTTPHEADER, $header_send);

// Don't return HTTP headers. Do return the contents of the call
//curl_setopt($session, CURLOPT_HEADER, ($headers == "true") ? true : false);

curl_setopt($session, CURLOPT_CUSTOMREQUEST, $method);
//curl_setopt($session, CURLOPT_FOLLOWLOCATION, true); 
//curl_setopt($ch, CURLOPT_TIMEOUT, 4); 
curl_setopt($session, CURLOPT_RETURNTRANSFER, true);

// Make the call
$response = curl_exec($session);
$info = curl_getinfo($session);
$header_size = curl_getinfo($session, CURLINFO_HEADER_SIZE);
$body = substr($response, $header_size);

if ($mimeType != "")
{
	// The web service returns XML. Set the Content-Type appropriately
	header("Content-Type: ".$mimeType);
}

//echo $body;
if (strcmp($headers,"true") == 0){
	echo $response;
}else{
	echo $body;
}

curl_close($session);

?>

