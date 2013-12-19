var sidebarOut = true, speed = 1000, 
	sidebarWidth = 275, arrowbarWidth = 35,
	tooltipHeight = 300, screenHeight = $(window).height(),
	screenWidth = $(window).width(), screenWidthSidebar = $(window).width() - sidebarWidth - arrowbarWidth;

$(document).ready(function() {
$(function() {
    $(".lobbySetSport").val($(".currentSelectedSport").attr('id'));
    $(".lobbySetStyle").val($(".currentSelectedStyle").attr('id'));
});
updateSize(screenWidthSidebar, screenHeight);


//changes the image and retracts the sidebar
$('#arrow img').click(function() {
	if (sidebarOut) {
		$('#sidestream').animate({left: -1*(arrowbarWidth+sidebarWidth)}, speed);
		
		setTimeout(function(){ 
			$('#arrow img').attr('src', '/static/images/right-arrow.png');
		},1000);
		updateSize(screenWidth, screenHeight);
        sidebarOut = false;
	}
	else {
		$('#sidestream').animate({left: 0}, speed);

		setTimeout(function(){ 
	        $('#arrow img').attr('src', '/static/images/left-arrow.png');
    	},1000);
		updateSize(screenWidthSidebar, screenHeight);
        sidebarOut = true;
	}
});

//when the mouse hovers near the edge of the screen bring out the arrow
$('#arrow-hover').mouseenter(  
  function () {
  	if(!sidebarOut){
	$('#sidestream').stop().animate({left: -1*sidebarWidth}, speed);  
	$('#arrow-hover').hide();
	}
  });

//retract arrow if the user doesn't want it
$('#arrow').mouseleave(  
  function () {
  	if(!sidebarOut){
	$('#sidestream').stop().animate({left: -1*(arrowbarWidth+sidebarWidth)}, speed);
	$('#arrow-hover').show();
	}
});

//More information window
$('.card').click(function() {
	if($('.active')[0] != this){
	if($('.active')[0]){
		$('.active').find(">:first-child").hide();
		$('.active').removeClass('active');
	}
		console.log(prettify($(".thisDate").attr('id')));
		$(".fillDate").html(prettify($(".thisDate").attr('id')));
		$(this).addClass('active');
		if(screenHeight > 500){
			if(screenHeight - $(this).offset().top > 250){
				$(this).find(">:first-child").css("top", $(this).offset().top - tooltipHeight/2  + 25+ "px");		
			}
			else{	
				$(this).find(">:first-child").css("top", screenHeight - 500 + "px");
			}
		}
		$(this).find(">:first-child").toggle();
	}
	else{
		$('.active').find(">:first-child").hide();
		$('.active').removeClass('active');
	}
});

//More information window
$('#add-game-button').click(function() {
	$('.add-game-cont').toggle();
	$('#add-game-screen').toggle();
});

//More information window
$('.close-button').click(function() {
	$('.add-game-cont').toggle();
	$('#add-game-screen').toggle();
});

$('.switchToProfile').click(function() { switchToProfile(); });
$('.switchToProfileDir').click(function() { 
	
	switchToProfile(); 
	});
$('.switchToLobby').click(function() { switchToLobby(); });
$('.switchToGame').click(function() { switchToGame(); });

function switchToProfile()
{
	if($('#game').is(":visible")){
	$('#game').fadeOut(500);
	}
	if($('#lobby').is(":visible")){
	$('#lobby').fadeOut(500);
	}
	setTimeout(function(){$('#profile').fadeIn(500);}, 500);	
}

function switchToLobby()
{
	if($('#profile').is(":visible")){
	$('#profile').fadeOut(500);
	}
	if($('#game').is(":visible")){
	$('#game').fadeOut(500);
	}
	setTimeout(function(){$('#lobby').fadeIn(500);}, 500);	
}

function switchToGame()
{
	if($('#lobby').is(":visible")){
	$('#lobby').fadeOut(500);
	}
	if($('#profile').is(":visible")){
	$('#profile').fadeOut(500);
	}
	setTimeout(function(){$('#game').fadeIn(500);}, 500);
}

function updateSize(width, height){
	$('#profile').height(height);	
	$('#lobby').height(height);	
	$('#game').height(height);
	$('#profile').animate({width: width}, speed);
	$('#lobby').animate({width: width}, speed);
	$('#game').animate({width: width}, speed);
}

function SelectElement(valueToSelect)
{    
    var element = $('.lobby'+valueToSelect);
    console.log(element);
    console.log(element.select());
}

//2013-01-01T01:00
function prettify(input){
	var array = input.split('-');
	var year = array[0];
	var month = array[1];
	array = array[2].split('T');
	var day = array[0];
	var time = array[1];
	var output_date = getMonth(month) + " "+day+", "+year+" at "+time;
	return output_date;
}

function getMonth(input){
	input = parseInt(input);
	input = input - 1;
	var month=[];
	month[0]="January";
	month[1]="February";
	month[2]="March";
	month[3]="April";
	month[4]="May";
	month[5]="June";
	month[6]="July";
	month[7]="August";
	month[8]="September";
	month[9]="October";
	month[10]="November";
	month[11]="December";

	return month[input];
}
});

$(window).resize(function() {
screenHeight = $(window).height();
screenWidth = $(window).width();
screenWidthSidebar = $(window).width() - sidebarWidth - arrowbarWidth;
$('#search-field').height(screenHeight);
if(!sidebarOut){
	$('#profile').width(screenWidth);	
	$('#lobby').width(screenWidth);	
	$('#game').width(screenWidth);	
}
else{
	$('#profile').width(screenWidthSidebar);	
	$('#lobby').width(screenWidthSidebar);	
	$('#game').width(screenWidthSidebar);	
}
});