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
function validateYouTubeUrl(url) {
        if (url != undefined || url != '') {
            var regExp = /^.*(youtube\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|\?v=)([^#\&\?]*).*/;
            var match = url.match(regExp);
            if (match && match[2].length == 11) {
                // Do anything for being valid
                // if need to change the url to embed url then use below line
                return 'https://www.youtube.com/embed/' + match[2] + '?autoplay=0';
            }
            else {
                return false
            }
        }
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
                showdown.setFlavor('github')
                var converter = new showdown.Converter(),
                    html = converter.makeHtml(val[key1]['content'])
                const parser = new DOMParser()
                var t = parser.parseFromString(html, 'text/html')
                z.appendChild(t.documentElement)
                for (key2 of Object.keys(val[key1]['attachments'])) {
                    //console.log(val[key1]['attachments'][key2]['url'])
                    var img = document.createElement("img")
                    img.src = val[key1]['attachments'][key2]['url']
                    img.width = "640"
                    var br = document.createElement("br")
                    z.appendChild(br)
                    z.appendChild(img)
                }
                for (key2 of Object.keys(val[key1]['links'])) {
                    if(validateYouTubeUrl(val[key1]['links'][key2])) {
                        var yt = document.createElement("iframe")
                        yt.src = validateYouTubeUrl(val[key1]['links'][key2])
                        yt.width = "640"
                        yt.height = "360"
                        yt.frameBorder = "0"
                        yt.allowFullscreen = "1"
                        console.log(val[key1]['links'][key2])
                        var br = document.createElement("br")
                        z.appendChild(yt)
                    }
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