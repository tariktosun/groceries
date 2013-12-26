$(document).ready(function(){
    
    //  USER CREATION FORM INTERACTIONS

    //  Netid form focus
    $('.netidform').focus(function(){
        
        //  If the form still has its default value
        if (this.value == "netid") {
            $('.netidform').css("color", "black");
            $('.netidform').attr("value", "");
        }
    });

    //  Netid form deselect
    $('.netidform').blur(function(){
        
        // If the user did not enter text
        if (this.value == "") {
            $('.netidform').css("color", "#ccc");
            $('.netidform').attr("value", "netid");
        }
    });

    //  Firstname form focus
    $('.firstform').focus(function(){
        if (this.value == "first name") {
            $('.firstform').css("color", "black");
            $('.firstform').attr("value", "");
        }
    });

    //  Firstname form deselect
    $('.firstform').blur(function(){
        if (this.value == "") {
            $('.firstform').css("color", "#ccc");
            $('.firstform').attr("value", "first name");
        }
    });

    //  Lastname form focus
    $('.lastform').focus(function(){
        if (this.value == "last name") {
            $('.lastform').css("color", "black");
            $('.lastform').attr("value", "");
        }
    });

    //  Lastname form deselect
    $('.lastform').blur(function(){
        if (this.value == "") {
            $('.lastform').css("color", "#ccc");
            $('.lastform').attr("value", "last name");
        }
    });
});
