"use strict"

jQuery.isSubstring = function(haystack, needle) {
    return haystack.indexOf(needle) !== -1;
};

var initHandlers = function () {

    $("#like-button").on("click", function(event) {
        var $url = $(this).attr("data-cat-url"),
            resultRegex = /[0-9]*[\ \t]+likes{1}/;

        $button = $.get($url, function(data) {
            var string = data.match(resultRegex)[0]
            if(string !== null || string !== undefined) {
                data = string;
            } else {
                data = "0 likes";
            }

            $("#like-count").html(data);
            $("#like-button").hide();
        });

    });

    $('#suggestion').keyup(function() {
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data){
            $('#cats').html(data);
        });
    });

};

$(document).ready(function () {
    console.log("Rango AJAX running.");
    initHandlers();
});