$(window).load(function() {
    $('#startLoader').hide();
    
    calculateHeight();
});

$(window).resize(calculateHeight);

$(document).ready(function(){
	var showHeaderAt = 80;
	$(window).on('scroll', function(e){
		if($(window).scrollTop() > showHeaderAt) {
			$('body').addClass('fixed');
		} else {
			$('body').removeClass('fixed');
		}
	});
});

function calculateHeight() {
	console.log($(window).height());
	console.log($(".header-fixed").outerHeight());
	console.log($(".footer").outerHeight());
	
	var height = $(window).height() - $(".header-fixed").outerHeight() - $(".footer").outerHeight() - 15 - 10 - 20 -75;
	
	$(".sortable").height(height);
	$(".section").height(height + 120);
}