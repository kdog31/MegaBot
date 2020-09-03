var table = document.createElement("table");
var servers = {};
var channels = {};

function getServers() {
    $.getJSON('/api/servers', function(data) {
        $("#server").empty()
        $.each( data, function(key, val) {
            var sel = document.getElementById('server');
            var opt = document.createElement('option')
            servers[key] = val
            opt.appendChild(document.createTextNode(key))
            opt.value = val
            sel.appendChild(opt)
        });
        $("#channel").empty()
        getChannels(document.getElementById('server').value)
    });
}
function getChannels(server) {
    url = "/api/servers/" + server
    $.getJSON(url, function(data) {
        $.each(data, function(key, val) {
            if (key == "channels") {
                for (var key1 of Object.keys(val)) {
                    var sel = document.getElementById('channel');
                    var opt = document.createElement('option');
                    opt.appendChild(document.createTextNode(val[key1]))
                    opt.value = key1
                    sel.appendChild(opt)
                }
                getMessages()
            };
        });
    });
}
function getMessages() {
    url = "/api/servers/" + document.getElementById("server").value + "/" + document.getElementById("channel").value + "?len=" + document.getElementById("quantity").value
    //console.log(url)
    $.getJSON(url, function(data) {
        $.each(data, function(key, val) {
            //console.log(key, val)
            for (key1 of Object.keys(val)) {
                //console.log(key1, val[key1]['author']['author_displayname'], val[key1]['content'])
                var x = document.getElementById("messages")
                var y = document.createElement("tr");
                y.setAttribute("id", key1)
                document.getElementById("messages").appendChild(y)
                var z = document.createElement("td")
                var t = document.createTextNode(val[key1]['author']['author_displayname'] + ": ")
                z.appendChild(t)
                var t = document.createTextNode(val[key1]['content'])
                z.appendChild(t)
                for (key2 of Object.keys(val[key1]['attachments'])) {
                    //console.log(val[key1]['attachments'][key2]['url'])
                    var img = document.createElement("img")
                    img.src = val[key1]['attachments'][key2]['url']
                    var br = document.createElement("br")
                    z.appendChild(br)
                    z.appendChild(img)
                }
                document.getElementById("messages").appendChild(z)
            }
        })
    })
}

document.addEventListener('input', function (event) {
    if (event.target.id !== 'server') return;
    $("#messages").empty()
    getChannels(document.getElementById('server').value)
    $("#channel").empty()
})
document.addEventListener('input', function (event) {
    if (event.target.id !== 'channel') return;
    $("#messages").empty()
    getMessages()
})
document.addEventListener('input', function (event) {
    if (event.target.id !== 'quantity') return;
    $("#messages").empty()
    getMessages()
})

$(document).ready(getServers())