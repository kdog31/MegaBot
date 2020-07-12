function stats() {
    var items = {};
    $.getJSON( "/api/stats", function( data ) {
        $.each( data, function( key, val ) {
          items[key] = val
        });
        document.getElementById("stats").innerHTML = "Megabot is managing " + items['users'] + " users across " + items['servers'] + " servers"
    });
}

$(document).ready(stats())