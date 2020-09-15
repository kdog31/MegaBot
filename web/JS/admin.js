var inputs = {}
var a

function GenerateSecret() {
    var token = document.getElementById("token").value
    inputs['token'] = token
    $.post('/admin/token', JSON.stringify(inputs), function(){cookie = "token="+token; document.cookie = cookie; ok()});
    document.getElementById("incorrect").innerHTML = "Invalid Passcode"
}

function ok() {
    window.location.replace('/admin/console')
}
function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}
document.addEventListener('click', function (event) {
    if (event.target.id !== 'generate') return;
    GenerateSecret()
    inputs = {}
})