$(document).ready(function(){


    //  USER INTERACTION WITH PROMPTS
    
    //  On post prompt focus
    $('.postPrompt').focus(function(){
        
        //  If the prompt still has the default value
	if (this.value == "Post new message") {
	    $(this).css("height", "40px");
	    $('.submitButton', this).css("display", "inline");
	    $(this).css("color", "black");
	    $(this).attr("value", "");
	}
    });    
    
    //  On post prompt deselect
    $('.postPrompt').blur(function(){

        //  If the user did not enter text
	if (this.value == ""){
	    $(this).css("color", "#ccc");
	    $(this).attr("value", "Post new message");
	}
    });
    
    //  On comment prompt focus
    $('.commentPrompt').focus(function(){
	if (this.value == "Write a comment...") {
	    $(this).css("height", "40px");
	    $('.submitButton', this).css("display", "inline");
	    $(this).css("color", "black");
	    $(this).attr("value", "");
	}
    });

    //  On comment prompt deselect
    $('.commentPrompt').blur(function(){
	if (this.value == ""){
	    $(this).css("color", "#ccc");
	    $(this).attr("value", "Write a comment...");
	}
    });

    //  On search prompt focus
    $('.searchBox').focus(function(){
	if (this.value == "Search") {
	    $('.submitButton', this).css("display", "inline");
	    $(this).css("color", "black");
	    $(this).attr("value", "");
	}
    });
    
    //  On search prompt deselect
    $('.searchBox').blur(function(){
	if (this.value == ""){
	    $(this).css("color", "#ccc");
	    $(this).attr("value", "Search");
	}
    });


    //  OTHER USER INTERACTIONS

    
    //  When user clicks on a post
    $('.content-container').click(function(event){
        
        //  Display the comment prompt associated with the post
        var target = event.target;
	currentContainer = this;
	currentComment = $('.commentBox', this);
	if($(target).is(".action")){
	    $('.commentBox', this).css("display", "block");
	}

    });
    
    //  When the user presses return inside any form, submit the form
    $('form').keypress(function(e){
	if (e.which == 13){
	    e.preventDefault();
	    this.submit();
	}
    }); 
    
    
    //  DYNAMIC RENDERING OF HASHTAG LINKS
    

    //  For each instance of a class containing hashtags
    $('.posttext, .comment, .hashtag').each(function(){
	
        //  Function to find hashtags and add links to them
	function hashTagFilter(post){    
	    function linkify(match){
		return "<a href=/" + match.substring(1) + "/ class='hashtag'>" + match + "</a>";
	    }
	    return post.replace(/#([-_a-zA-Z0-9]{1,24})/gi, linkify); 
	}

        //  Replace the current value of the class instance with the same value
        //  and a link
	var val = $(this).html();
	val = hashTagFilter(val);
	$(this).html(val);	
    });
    
    
    //  DYNAMIC RENDERING OF AT MENTION LINKS
    

    //  For each instance of a class containing at mentions
    $('.posttext, .comment').each(function(){
	
        //  Function to find at mentions and add links to them
	function atFilter(post){
	    function linkify(match){
		return "<a href=/user/" + match.substring(1) + "/ class='atMention'>" + match + "</a>";
	    }
	    return post.replace(/[@]([a-zA-Z]+)[-]([a-zA-Z]+)/gi, linkify);
	}

        //  Replace the current value of the class instance with the
        //  same value and a link
	var val = $(this).html();
	val = atFilter(val);
	$(this).html(val);	
    }); 
});
