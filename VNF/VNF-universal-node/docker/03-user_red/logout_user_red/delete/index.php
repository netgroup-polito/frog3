<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>  
	<title>Logout from the Unify network</title>
	<link rel="stylesheet" href="delete_css/style.css">
	<script>
		var ip = "<?php echo $_SERVER['SERVER_ADDR']; ?>";
		var s = window.location.href;
		s = s.split("//")[1].split("/"); 
		console.log(s[0]);
		ip = s[0];
	</script>
	<script src="delete_js/script.js"></script>  
</head>
<body>

	<div id="page">	

		<!-- TOP BAR -->
		<div id="top-bar">	
		</div> <!-- end TOP BAR -->

		<!-- HEADER -->
		<div id="header">
			<div class="page-full-width cf">
				<div id="login-intro" class="fl">
					<h1>Logout from the <strong>Unify</strong> network</h1>
					<h5>Enter your credentials below</h5>
				</div>
			</div>
			<div class="page-full-width cf">
				<div id="afterlogin-intro" class="fl" style="display:none;">
					<h1>Logout from the <strong>Unify</strong> network</h1>
					<h5>Success!</h5>
				</div>					
			</div>
		</div>  <!-- end HEADER -->
			
		
		<!-- MAIN CONTENT -->
		<div id="content">	
			
			<div id="login_ok" style="display:yes;" align="center">			
				<br>
				<h1 align= "center" id="logged">You are logged in the UNIFY network.</h1>
				<br>
				
				<div id="logout_button">
					<input id="button_logout" type="button" onClick="deleteProfile();" name="logout" id="logout" class="button round blue image-right ic-right-arrow" value="LOGOUT">
					<div id="logout" style="display:none;">
						<h1 >You are successfully logged out</h1>
					</div>
				</div>
				<br><br><br>
				<img src="unify.png" alt="Unify" style="width:100%; /* you can use % */ height: auto;">
				
			</div>
			
		</div> <!-- end content -->
		

		

	</div> <!-- end PAGE -->

</body>
</html>
