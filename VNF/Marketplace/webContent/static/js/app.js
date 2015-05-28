$(function(){
	$( "#sortable1" ).sortable();
	$( "#sortable1" ).disableSelection();
	
	$(".navbar-btn").bind("click",function (event) {
		$('#startLoader').show();
	});
	
	$("#submit_button").bind("click",function (event) {
		var csrftoken = $.cookie("csrftoken");
		var checked_app = $(".check_app:checked").serialize(); 
		$('#startLoader').show();
		
		$.ajax({
			type: "POST",
			url: "/app/",
			data: {psa_active: checked_app, csrfmiddlewaretoken: csrftoken},
			success: function(data) {
				$('#startLoader').hide();
				$("#response_message").removeClass("messageSuccess messageError");
				$('#response_message').show();
				$("#response_message").html("Customization saved");
				$("#response_message").addClass("messageSuccess");
				saved = true;
				setTimeout(function() { $('#response_message').hide(800); }, 5000 );
			},
			error: function(data, status) {
				if(data.status == 401) 
					window.location.href = "/login/";
				$('#startLoader').hide();
				$("#response_message").removeClass("messageSuccess messageError");
				$('#response_message').show();
				$("#response_message").html("Error saving customizations");
				$("#response_message").addClass("messageError");
				setTimeout(function() { $('#response_message').hide(800); }, 5000 );
			},
		});
	});
});