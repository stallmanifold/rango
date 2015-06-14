var main = function() {
    $("#about-btn").click( function(event) {
        alert("You clicked the button using JQuery!");
    });

    $("p").hover(function () {
        $(this).attr('old_color', $(this).css('color'))
        $(this).css('color', 'violet');
    }, function () {
        $(this).css('color', $(this).attr("old_color"))
        $(this).attr('old_color', '').removeAttr('old_color')
    });

    $("#about-btn").addClass('btn btn-primary')
}

$(document).ready(function() {
    main();
});
