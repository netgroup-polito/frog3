<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
		<title>Home</title>	
	</head>
	<body>
		<?php

			// Reading configuration file
			$ini_array = parse_ini_file("config.ini", true);
			if(!isset($ini_array['keystone']['ip']) || !isset($ini_array['keystone']['port'])){
				print("configuration error");
				exit(-1);
			}
			$keystone_ip = $ini_array['keystone']['ip'];
			$keystone_port = $ini_array['keystone']['port'];
			 
			
			include("include/rest.php");
			include("include/json_pretty_print.php");
			
			// User info
			if(!$_REQUEST['Username']||!$_REQUEST['Tenant']||!$_REQUEST['Password']){
				echo'
				<form name="info" action="index.php" method="post">
				<label>	Username:</label>
					<br />
					<input type="text" name="Username" size="30" class="inputbox" value="test" />
				<br /><br />
				<label>	Tenant:</label>
					<br />
					<input type="text" name="Tenant" size="30" class="inputbox" value="demo" />
				<br /><br />
				<label>	Password:</label>
					<br />
					<input type="text" name="Password" size="30" class="inputbox" value="test" />
				<br /><br />';
				echo '<h6><button class="button validate" type="submit">Get profile</button></h6>';
				
			} else if ($_REQUEST['Username']&&$_REQUEST['Tenant']&&$_REQUEST['Password']){
					
				// Come back to first page (choise user)
				echo "<a href = \"index.php\"><-- Select user</a></br></br></br>"; 
				
				// Login (get token)
				$url = "http://".$keystone_ip.":".$keystone_port."/v2.0/tokens";
				echo "GET TOKEN:<div style=\"margin-left:50px;margin-top:5px;\" >";

				$resp = CallAPI(POST, $url, "{\"auth\": {\"tenantName\": \"".$_REQUEST['Tenant']."\", \"passwordCredentials\": {\"username\": \"".$_REQUEST['Username']."\", \"password\": \"".$_REQUEST['Password']."\"}}}");
				echo "</div>";
				
				$obj = json_decode($resp);
				//echo $resp;
				$token = $obj->{'access'}->{'token'}->{'id'};
				$userID = $obj->{'access'}->{'user'}->{'id'};

				// Create profile
				if($_REQUEST['text']){
					$data = "";
					$url = "http://".$keystone_ip.":".$keystone_port."/v2.0/OS-UPROF/profile/users/".$userID;
					
					$stringa = str_replace(" ", "", stripslashes(strip_tags($_REQUEST['text'])));
					echo "CREATE PROFILE:<div style=\"margin-left:50px;margin-top:5px;\">";
					$resp = CallAPI(POST, $url, $stringa, $token);
					echo "</div>";
				}
				
		
				$data = "";
				$url = "http://".$keystone_ip.":".$keystone_port."/v2.0/OS-UPROF/profile/users/".$userID;
				echo "GET PROFILE:<div style=\"margin-left:50px;margin-top:5px;\">";
				$resp = CallAPI(GET, $url, false, $token);
				echo "</div>";

				if($resp != 404){	
					$obj = json_decode($resp);
					$resp = json_encode($obj->{'profile'}->{'graph'});
					echo'</br></br>Last midified date:&nbsp;';
					echo json_encode($obj->{'profile'}->{'timestamp'});
					$resp = prettyPrint($resp);
					$formatted = nl2br($resp);
					$lines_arr = preg_split('/\n|\r/',$resp);
					$num_newlines = count($lines_arr); 
				} else {
					$resp = "";
				}
				echo '<h2>Username:<br>'.$_REQUEST['Username'].'<h2>';
				echo '<form name="invia" action="index.php" method="post">';
				echo '
				<input type="hidden" name="Username" value="'.$_REQUEST['Username'].'">
				<input type="hidden" name="Tenant" value="'.$_REQUEST['Tenant'].'">
				<input type="hidden" name="Password" value="'.$_REQUEST['Password'].'">
				';
				echo "<textarea name=\"text\" class=\"messaggio\" rows=\"".($num_newlines+3)."\" cols=\"150\">".stripcslashes($resp)."</textarea>";
				echo '<h6><button class="button validate" type="submit">Update profile</button></h6>';
				echo '</form>';
			
			}
		?>
	</body>
</html>
