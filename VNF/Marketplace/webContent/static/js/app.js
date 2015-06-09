$(function(){
	var saved = true;
	
	$(".applist").sortable();
	
	$(".navbar-btn").bind("click",function (event) {
		$('#startLoader').show();
	});
	
	$("a").bind("click", function (event) {
		if( saved == false ) {
			$('#startLoader').hide();
			return confirm("All changes will be lost, do you want to proceed anyway?");
		}
	});
	
	$(".btn-radio").bind("click", function(event) {
		if($(this).hasClass("btn-grey")) {
			$(this).toggleClass("btn-blue btn-grey");
			$(this).siblings(".btn-radio").toggleClass("btn-blue btn-grey");
			if( $(this).hasClass("btn-radio-left") ) {
				$(this).siblings(".app_input").val(1);
			} else {
				$(this).siblings(".app_input").val(0);
			}
			
			saved = false;
		}
	});
	
	$(".o-modal").bind("click", function(event) {
		$("[name='config']").val("");
		console.log($(this).find(".btn"));
		$("[name='psa-id']").val($(this).find(".btn").attr("id"));
	});
	
	$("#submit_button").bind("click",function (event) {
		var csrftoken = $.cookie("csrftoken");
		var checked_app = $(".app_input").serialize();
		$('#startLoader').show();
		
		$.ajax({
			type: "POST",
			url: "/app/",
			data: {psa_active: checked_app, csrfmiddlewaretoken: csrftoken},
			success: function(data) {
				console.log(data);
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