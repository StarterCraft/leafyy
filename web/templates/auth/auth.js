function finishVerification(data) {
    if (data.verified)
        window.location = $(".hidden#redirectAfter").text();
    else return false;
}

function verifyToken() {
    token = getCookie('X00', null);
    if (token !== null)
        $.ajax({
            //убрать это уродство! использовать здесь тело запроса!
            url: "/token/verify?token=" + token,
            method: "GET",
            success: finishVerification,
            error: function(error) {
                console.error('Error:', error);
            }
        })
}

verifyToken();

function finishLogin(data) {
    if (data.access_token && data.refresh_token) {
        Cookies.set('X00', data.access_token);
        Cookies.set('X01', data.refresh_token);
        window.location = $(".hidden#redirectAfter").text();
    } else {
        setStatus('Неверное имя польователя или пароль!');
    }
}

function login(event) {
    event.preventDefault();

    console.log("Login begins...");

    var username = $('#login').val();
    var password = $('#password').val();

    console.log('Creds:', username, password);

    var fdata = new FormData();
    fdata.append("username", username);
    fdata.append("password", password);

    $.ajax({
        url: '/token',
        method: 'POST',
        contentType: 'application/x-www-form-urlencoded',
        data: fdata,
        success: finishLogin,
        error: function(error) {
            console.error('Error:', error);
        }
    });
}

function prepare() {
    //$("#loginForm").on("submit", login);
}

$(document).ready(prepare);
