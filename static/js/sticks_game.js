var gameplayTemplate = "<div class='alert alert-%(alert) gameplay-entries' role='alert' style='display: none;'>%(player) took %(number) stick%(s). The pile now has %(total)</div>";

$(document).ready(function(){
    var total = parseInt($("#sticks-number").text());
    bindEvents();
    populateInstructions(total);
    configurePlayButtons(total);
});

function bindEvents(){
    // Playing buttons event binding
    $("#play-buttons > button").on("click", play);
    
    // Number keys event binding
    $(document).keydown(function(e){
        //Include hook for those browsers that don't support the 'key' property yet
        var key = e.key || {49: "1", 50: "2", 51: "3"}[e.keyCode];
        if("123".indexOf(key) >= 0){
            var btn = $("button:contains("+key+")");
            if(!btn.prop("disabled"))
                btn.click();
        }
    });

    // Enable modal accepting through Enter key
    $("#end-modal").keydown(function(e){
        if(e.keyCode == 13)
            $("#end-modal .btn-primary").click();
    });

}

function populateInstructions(total){
    var sticksHtml = "";
    for(var i = 0; i < total; i++){
        sticksHtml += "<div class='stick-drawing'></div>";
    }
    $("#sticks-panel").append(sticksHtml);
}

// Disables buttons that can't be played
function configurePlayButtons(total){
    if(total < 3){
        $("#play-buttons > button").slice(Math.max(0, total) - 3).prop("disabled", true);
    }
}

function decrementPile(number){
    var total = parseInt($("#sticks-number").text()) - number;
    $("#sticks-number").text(total);
    $(".stick-drawing").slice(total).fadeOut("normal", function() { $(this).remove();} );
    configurePlayButtons(total);
}

function play(){
    var not_disabled_buttons = $("#play-buttons > button:not([disabled])");
    not_disabled_buttons.prop( "disabled", true );
    var number = parseInt($(this).text());
    decrementPile(number);
    $.ajax({
        url: '/play',
        data: { 'number': number.toString()},
        type: 'POST',
        success: function(response) {
            if(response.endOfGame){
                var youLost = response.loser == 'You';
                if(!youLost){
                    decrementPile(response.number);
                    addGameplay("Computer", response.number);
                    $('#dialog-message-details').hide();
                }
                $('#dialog-message-headline').text("You % the game".replace('%', youLost ? 'lost' : 'won'));
                $('#end-modal').modal('show');
            }else{
                not_disabled_buttons.prop("disabled", false);
                decrementPile(response.number);
                addGameplay("Computer", response.number);
            }
        },
        error: function(error) {
            var errorMessage = error.status == 401 ? error.responseText : "Could not communicate with the server";
            alert(errorMessage + " Try to refresh the page.");
        }
    });
    addGameplay("You", number);
}

function addGameplay(player, number){
    if($("#gameplay > .alert").length > 9){
        $("#gameplay > .alert:first").fadeOut("normal", function() { $(this).remove();} );
    }
    $(gameplayTemplate.replace("%(alert)", player == "Computer" ? "computer" : "player").replace("%(player)", player).replace("%(number)", number).replace("%(s)", number > 1 ? "s" : "").replace("%(total)", $("#sticks-number").text())).appendTo("#gameplay").fadeIn();
}
