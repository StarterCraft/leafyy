$(document).ready(function() {
    $('#loginForm').on('submit', function(event) {
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
                if (data.access_token) {
                    document.cookie = 'access_token=' + data.access_token + '; path=/';
                    window.location.href = '/';
                } else {
                    setStatus('Incorrect username or password.');
                }
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });
});