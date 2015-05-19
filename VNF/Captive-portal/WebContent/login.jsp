<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>  
	<title>Login to your FROG network</title>
	<link rel="stylesheet" href="css/style.css">
	<script src="js/script.js"></script>  
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
					<h1>Login to <strong>your</strong> FROG network</h1>
					<h4>Enter your credentials below</h4>
				</div>
			</div>
			<div class="page-full-width cf">
				<div id="afterlogin-intro" class="fl" style="display:none;">
					<h1>Login to <strong>your</strong> FROG network</h1>
					<h4>Success!</h4>
				</div>					
			</div>
		</div>  <!-- end HEADER -->
			
		
		<!-- MAIN CONTENT -->
		<div id="content">	
			<form action="#" method="" id="login-form">	
				<fieldset>
					<p>
						<label for="login-username">username:</label>
						<input type="text" placeholder="Username" name="username" id="input-username" class="round full-width-input" autofocus maxlength="32" onKeyPress="submitonenter('submit',event,this)" />
					</p>

					<p>
						<label for="login-password">password:</label>
						<input type="password" placeholder="Password" name="password" id="input-password" class="round full-width-input" maxlength="32" onKeyPress="submitonenter('submit',event,this)"/>
					</p>

					<p>
						&nbsp;
					</p>
					
					<input type="button" onClick="sendLoginRequest();" name="submit" id="submit" class="button round blue image-right ic-right-arrow fr" value="LOGIN">
				</fieldset>

<!--				
				<br/><div><a href="register.htm"><h3 style="text-decoration:underline;">Create a new account<h3></a></div>
-->				
				<br/><div id="error-msg" class="error-box round"> </div>

<!--				
				<br/><div class="information-box round">Just click on the "LOGIN" button to continue, login as "guest/guest" if you do not have an account.</div>
-->
			</form>		
			
			<div id="message" style="display:none;" align="center"> Loading...</div>
			
			<div id="login_ok" style="display:none;" align="center">			
				<br>
				<h1 align= "center"><b>Congratulations!</b></h1>
				<br>
				<h1 align= "center">You have been successfully logged in your FROG network.</h1>
				<br>
				
				<div id="logout_button" align="center">
					<input type="button" onClick="sendLogoutRequest();" name="logout" id="logout" class="button round blue image-right ic-right-arrow" value="LOGOUT">
				</div>
				
			</div>
			
		</div> <!-- end content -->
		

		<!-- FOOTER -->
		<div id="footer">
			<p>&copy; Copyright 2013-2015 <a href="http://www.polito.it">Politecnico di Torino</a>. All rights reserved.</p>	
		</div>
		<!-- end footer -->

	</div> <!-- end PAGE -->

</body>
</html>
