$(function() {
  	var saved = true;
  	
  	$( "ul.sourceList" ).sortable({
    	connectWith: "ul",
    });
 
    $( "ul.targetList" ).sortable({
    	connectWith: "ul",
    	cancel: ".empty-placeholder",
    	receive: function( event, ui ) {
    		console.log(event);
    		console.log(ui.item);
    		numItems = $(".targetList").find('li').length;
    		if(numItems==2){
				$(".targetList").find('li.empty-placeholder').hide();
			}
			saved = false;
    	},
    	remove: function( event, ui ) {
    		numItems = $(".targetList").find('li').length;
    		if(numItems==1){
				$(".targetList").find('li.empty-placeholder').show();
			}
			saved = false;
    	}
    });
 
    $( "#sortable1, #sortable2" ).disableSelection();
    
    $("a#logout").bind("click",function (event) {

		if($(".targetList").find('li').length > 1 && saved == false) {
			$('#startLoader').hide();
			var response = confirm("All changes will be lost, do you want to proceed anyway?");
			if(response == false) {
				return false;
			}
		}
		
		return true;
	});
	
	$(".navbar-btn").bind("click",function (event) {
		$('#startLoader').show();
	});
	
	$("#submit_button").bind("click",function (event) {
		var ser = $( "#sortable2" ).sortable("serialize", {expression: /(.+?)_(.+)/});
		var csrftoken = $.cookie("csrftoken");
		
		$('#startLoader').show();
		
		$.ajax({
			type: "POST",
			url: "/store/",
			data: {psa_ser: ser, csrfmiddlewaretoken: csrftoken},
			success: function(data) {
				$('#startLoader').hide();
				$("#response_message").removeClass("messageSuccess messageError");
				$('#response_message').show();
				$("#response_message").html("Customization saved");
				$("#response_message").addClass("messageSuccess");
				saved = true;
				setTimeout(function() { $('#response_message').hide(800); }, 5000 );
			},
			error: function(data) {
				console.log(data);
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