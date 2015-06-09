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
	var height = $(window).height() - $(".header-fixed").height() - $(".footer").height() - 150;
	
	if($(window).height() > 600) {
		$(".sortable").height(height);
		$(".section").height(height + 120);
	}
}