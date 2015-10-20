<?php
// Method: POST, PUT, GET etc
// Data: array("param" => "value") ==> index.php?param=value

function CallAPI($method, $url, $data = false, $token = false)
{
    $curl = curl_init();
    switch ($method)
    {
        case "POST":
			echo"Request:</br> POST";
            curl_setopt($curl, CURLOPT_POST, 1);
            if ($data)	
                curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
            break;
        case "PUT":
			echo"Request:</br> PUT";
			curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "PUT"); 
			curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
            //curl_setopt($curl, CURLOPT_PUT, 1);
			if ($data)	
                curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
            break;
        default:
			if($method == "GET") echo"Request:</br> GET";
            if ($data)
                $url = sprintf("%s?%s", $url, http_build_query($data));
    }

    if($token)
		curl_setopt($curl, CURLOPT_HTTPHEADER, array("Content-Type: application/json", "Accept: application/json","X-Auth-Token: ".$token));
	else
		curl_setopt($curl, CURLOPT_HTTPHEADER, array("Content-Type: application/json"));
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_VERBOSE, 1);
	curl_setopt($curl, CURLOPT_HEADER, 1);
	$response = curl_exec($curl);
	$info = curl_getinfo($curl);
	$header_size = curl_getinfo($curl, CURLINFO_HEADER_SIZE);
	$header = substr($response, 0, $header_size);
	echo '</br></br>Response:</br>'.$header.'</br></br></br>';
	$body = substr($response, $header_size);
	if (empty($info['http_code']) || strcmp($info['http_code'], 404) == 0) {
		return 404;
	}
	
    return $body;
}
?>