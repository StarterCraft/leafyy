let refreshingRst = false;

function finishVerificationFinale(data) {
    if (data.access_token && data.refresh_token) {
        Cookies.set("X00", data.access_token);
        Cookies.set("X01", data.refresh_token);
        refreshingRst = true;
    }
    else {
        console.log(data);
    }
}

function tryRefreshToken() {
    var refreshToken = getCookie('X01', null);

    if (!refreshToken) return false;

    $.ajax({
        url: "/token/refresh",
        method: "POST",
        data: {refresh_token: refreshToken},
        success: finishVerificationFinale,
        error: function(error) {
            console.error('Error:', error);
        }
    })
}

function finishVerification(data) {
    if (!data.verified) {
        tryRefreshToken();
        if (!refreshingRst) {
            window.location.replace("/auth/login?to=" + $("#redirectAfter").text());
        }
    }
    else {
        window.location.replace($("#redirectAfter").text() + "?token=" + getCookie("X00"))
    }
}

function verifyToken() {
    token = getCookie('X00', null);
    if (token)
        $.ajax({
            //убрать это уродство! использовать здесь тело запроса!
            url: "/token/verify?token=" + token,
            method: "POST",
            //data: {token: token},
            success: finishVerification,
            error: function(error) {
                console.error('Error:', error);
            }
        })
    else {
        window.location.replace("/auth/login?to=" + $("#redirectAfter").text());
    }
}

$(document).ready(verifyToken());
