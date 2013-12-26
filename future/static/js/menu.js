$(document).ready(function(){
    
    // When the user clicks the menu posting textarea
    $('textarea').focus(function(){
        
        //  If the textarea has its initial value
        if (this.value == "Post new menu") {
            $('.submitButton').css("display", "block");
            $('textarea').css("height", "120px");
            $('textarea').css("color", "black");
            $('textarea').attr("value", "");
        }
    });

    // When the user clicks off of the textarea
    $('textarea').blur(function(){
        
        //  If the user did not enter text
        if (this.value == "") {
            $('.submitButton').css("display", "none");
            $('textarea').css("height", "20px");
            $('textarea').css("color", "#ccc");
            $('textarea').attr("value", "Post new menu");
        }
    });
});
