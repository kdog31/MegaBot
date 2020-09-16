function GetSettings() {
    url = "/admin/console/api?token=" + $.cookie('token')
    a = $.getJSON(url)
    $.getJSON(url, function(data) {
        $('#settings').empty()
        var settings = document.getElementById("settings")
        $.each(data, function(key, val){
            var title = document.createElement("h4")
            var titlecontent = document.createTextNode(key)
            title.appendChild(titlecontent)
            settings.appendChild(title)
            var table = document.createElement("table")
            for (var key1 of Object.keys(val)) {
                var tr = document.createElement("tr")
                var td1 = document.createElement("td")
                var td2 = document.createElement("td")
                var button = document.createTextNode('\u274E')
                var entry = document.createTextNode(val[key1])
                var a = document.createElement("a")
                a.setAttribute("href", "#")
                a.setAttribute("onclick", "removesetting('"+key+"',"+key1+")")
                a.setAttribute("style", "text-decoration: none;")
                a.appendChild(button)
                td1.appendChild(a)
                td2.appendChild(entry)
                tr.appendChild(td1)
                tr.appendChild(td2)
                table.appendChild(tr)
            }
            var tra = document.createElement("tr")
            var intd = document.createElement("td")
            var intd2 = document.createElement("td")
            var add = document.createTextNode('\u2705')
            var box = document.createElement("input")
            var click = document.createElement("a")
            box.setAttribute("id", key)
            click.setAttribute("href", "#")
            click.setAttribute("onclick", "addsetting('"+key+"')")
            click.setAttribute("style", "text-decoration: none;")
            box.setAttribute("type", "text")
            click.appendChild(add)
            intd.appendChild(click)
            intd2.appendChild(box)
            tra.appendChild(intd)
            tra.appendChild(intd2)
            table.appendChild(tra)
            settings.appendChild(table)
        })
    })
}
function removesetting(key, index) {
    url = "/admin/console/api?token=" + $.cookie('token')
    $.getJSON(url, function(data) {
        data[key].splice(index, 1)
        console.log(data)
        $.post('/admin/console/api?token='+$.cookie('token'), JSON.stringify(data), function(){GetSettings()});
    })
}
function addsetting(key) {
    url = "/admin/console/api?token=" + $.cookie('token')
    $.getJSON(url, function(data) {
        newentry = document.getElementById(key).value
        data[key].push(newentry)
        $.post('/admin/console/api?token='+$.cookie('token'), JSON.stringify(data), function(){GetSettings()});
    })
}

$(window).on('load', function() {
    GetSettings()
    window.setInterval(function(){GetSettings()}, 5000);
});