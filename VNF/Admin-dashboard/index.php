<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=2.0"/>  
	<title>FROG Orchestrator Dashboard</title>
	<link rel="stylesheet" href="resources/css/style.css">
	<script>
		<?php include('config.php'); ?>
		var keystone_ip = "<?php echo $conf['keystone_ip']; ?>";
		var keystone_port = "<?php echo $conf['keystone_port']; ?>";
		var orchestrator_ip = "<?php echo $conf['orchestrator_ip']; ?>";
		var orchestrator_port = "<?php echo $conf['orchestrator_port']; ?>";
		var proxy_addr = "<?php echo $conf['proxy_addr']; ?>";
		var path = "<?php echo $conf['path']; ?>";
	</script> 
	<script src="resources/js/script.js">
	</script>
	
</head>
<body>

	<div id="page">	

		<!-- TOP BAR -->
		<div id="top-bar">	
		</div> <!-- end TOP BAR -->

		<!-- HEADER -->
		<div id="ranocchio">
			<div id="header">
	
				<div class="page-full-width cf">
					<div id="login-intro" class="fl">
						<h1 class="black_background">Instantiate network profile</h1>
						<h5 class="black_background">Customize your network</h5>
					</div>
				</div>
				<div class="page-full-width cf">
					<div id="afterlogin-intro" class="fl" style="display:none;">
						<h1 class="black_background">Login to the <strong>Unify</strong> network</h1>
						<h5 class="black_background">Success!</h5>
					</div>					
				</div>
			</div>  <!-- end HEADER -->
			
		
			<!-- MAIN CONTENT -->
		
			<div id="content"  style="overflow: hidden;">	
				<form action="#" method="" id="login-form">	
					<fieldset>
						<h1>
							<label>Authenticated access to the Internet</label>
							<input type="button" onClick="instantiateProfile('nobody','stack');" class="round " autofocus maxlength="32" name="submit" class="full-width-input button round blue image-right ic-right-arrow fr" value="enable">
							<input type="button" onClick="disinstantiateProfile('nobody','stack');" class="round " autofocus maxlength="32" name="submit" class="full-width-input button round blue image-right ic-right-arrow fr" value="disable">
						</h1>
						<!--
						<br>
						<h1>
							<label for="login-password">Protected access to the Internet</label>
							<input type="button" onClick="instantiateProfile('cisco-demo2','stack');" class="round " type="password"  name="submit" class="full-width-input button round blue image-right ic-right-arrow fr" maxlength="32" value="Instantiate profile">
							<input type="button" onClick="disinstantiateProfile('cisco-demo2','stack');" class="round " type="password"  name="submit" class="full-width-input button round blue image-right ic-right-arrow fr" maxlength="32" value="Delete profile">
	
						</h1>
						<br>
						<h1>
							<label for="login-password">Authenticated access to the Internet</label>
							<input type="button" onClick="instantiateProfile('nobody','stack');" class="round " type="password"  name="submit" class="full-width-input button round blue image-right ic-right-arrow fr" maxlength="32" value="Instantiate profile">
							<input type="button" onClick="disinstantiateProfile('nobody','stack');" class="round " type="password"  name="submit" class="full-width-input button round blue image-right ic-right-arrow fr" maxlength="32" value="Delete profile">
	
						</h1>
						-->
						
					</fieldset>
					<div id="loading">
					</div>				
					<br/><div id="error-msg" class="error-box round"> </div>
					
				</form>		

				
				<div id="login_ok" style="display:none;" align="center">			
					<br>
					<h1 align= "center"><b>Congratulations!</b></h1>
					<br>
					<h1 align= "center">Your profile is being instantiated.</h1>
					<br>
					
					<!-- <div id="logout_button" align="center">
						<input type="button" onClick="sendLogoutRequest();" name="logout" id="logout" class="button round blue image-right ic-right-arrow" value="LOGOUT">
					</div> -->
					
				</div>
				
				<div id="disinstantiated" style="display:none;" align="center">			
					<br>
					<h1 align= "center"><b>Congratulations!</b></h1>
					<br>
					<h1 align= "center">Your profile is being deleted.</h1>
					<br>
					
					<!-- <div id="logout_button" align="center">
						<input type="button" onClick="sendLogoutRequest();" name="logout" id="logout" class="button round blue image-right ic-right-arrow" value="LOGOUT">
					</div> -->
					
				</div>
				
			</div>
		</div> <!-- end content -->
		

		<!-- FOOTER -->
		<div id="footer">
			<p>&copy; Copyright 2013-2015 <a href="http://www.polito.it">Politecnico di Torino</a>. All rights reserved.</p>	
		</div> <!-- end footer -->

	</div> <!-- end PAGE -->

</body>
</html>
