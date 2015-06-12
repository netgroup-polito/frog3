$(function(){
	var saved = true;
	var timeout = null;
	
	$(".applist").sortable({
		axis: "y",
		delay: 900
	});
	
	$(".draggable").mousedown(function() {
		var obj = $(this);
		timeout = setTimeout(function() { obj.animate({backgroundColor: "#9D9D9D"}, 300) }, 300 );
	});
	
	$(".draggable").mouseup(function() {
		clearTimeout(timeout);
		$(this).animate({backgroundColor: "#C4C3C3"}, 500)
	});
	
	$(".navbar-btn").bind("click", function (event) {
		$('#startLoader').show();
	});
	
	$("a:not(.o-modal, .close)").bind("click", function (event) {
		if( saved == false ) {
			$('#startLoader').hide();
			return confirm("All changes will be lost, do you want to proceed anyway?");
		}
	});
	
	/* CONFIG MODAL WINDOW */
	$(".o-modal").bind("click", function(event) {
		var psa = $(this).find(".btn").attr("id");
		
		$.ajax({
			type: "GET",
			url: "/config/",
			data: {psa_id: psa},
			async: false,
			success: function(data) {
				$("[name='config-data']").val(data);
			},
			error: function(data, status) {
				return false;
			}
		});
		
		$("[name='psa_id']").val(psa);
	});
	
	/* SUBMIT APP ENABLED */
	$(".btn-submit").bind("click",function (event) {
		var csrftoken = $.cookie("csrftoken");
		var checked_app = $(".app-checked:checked").serialize();
		var ordered_app = $(".app-ordered").serialize();
		$('#startLoader').show();
		
		$.ajax({
			type: "POST",
			url: "/app/",
			data: {psa_active: checked_app, psa_ordered: ordered_app, csrfmiddlewaretoken: csrftoken},
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