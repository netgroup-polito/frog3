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
	var height = $(window).height() - $(".header-fixed").outerHeight() - $(".footer").outerHeight() - 120;
	
	if($(window).width() > 910) {
		$(".sortable").height(height);
		$(".section").height(height + 120);
		$( ".applist" ).sortable( "option", "delay", false );
	} else {
		$(".sortable").height('auto');
		$(".section").height('auto');
		$( ".applist" ).sortable( "option", "delay", 900 );
	}
}