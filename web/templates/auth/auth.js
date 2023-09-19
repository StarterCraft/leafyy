function finishLogin(data) {
    if (data.access_token && data.refresh_token) {
        Cookies.set('X00', data.access_token);
        Cookies.set('X01', data.refresh_token);
        window.location = $("#redirectAfter").text();
    } else {
        setStatus('Неверное имя польователя или пароль!');
    }
}

function login(event) {
    event.preventDefault();
    
    var username = $('#login').val();
    var password = $('#password').val();
    $.ajax({
        url: '/token',
        method: 'POST',
        contentType: 'application/x-www-form-urlencoded',
        data: {
            'username': username,
            'password': password
        },
        success: function(data) {
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
}

function prepare() {
    $('#loginForm').on('submit', login);
}

$(document).ready(prepare);
