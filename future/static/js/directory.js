$(document).ready(function(){
    
    //  When the user clicks the addFriend button
    $('.addFriend').click(function(){
        
        //  Pull the data necessary to make the request from HTML
        //  elements on the page
        var fbid = $(this).children('input').attr('value');
        var appid = $('#data').children('input').attr('value');
        
        //  Save the element for later access
        var clickedbutton = this;
        
        //  Initialize a facebook request
        FB.init({
            appId      : appid,
            status     : true, 
            cookie     : true,
            xfbml      : true
        });

        //  Send a facebook friend request
        FB.ui(
            { 
                method: 'friends.add', 
                id: fbid 
            }, 

            // Based on the how the user responded:
            function(param){
                //  If they sent the request
                if (param.action)
                {
                    $(clickedbutton).text("Request Sent");
                    $(clickedbutton).delay(1000).fadeOut('slow')
                }                
            }
        );
    });
 });
