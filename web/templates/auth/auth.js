function injectContent(response) {
    var redir = $("#redirectAfter").text();

    $("body").html(response);
    window.history.pushState({}, "Листочек", redir);
}

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
        contentType: "application/json",
        data: JSON.stringify({token: refreshToken}),
        success: finishVerificationFinale,
        error: function(error) {
            console.error('Error:', error);
            alert(error.responseText);
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
        $("#loading").text("Загрузка...");
        $.ajax({
            type: "GET",
            url: $("#redirectAfter").text(),
            headers: {"Authorization": "Bearer " + getCookie("X00", null)},
            success: injectContent
        });
    }
}

function verifyToken() {
    token = getCookie('X00', null);
    if (token)
        $.ajax({
            //убрать это уродство! использовать здесь тело запроса!
            url: "/token/verify",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({"token": token}),
            success: finishVerification,
            error: function(error) {
                console.error('Error:', error);
            }
        })
    else {
        window.location.replace("/auth/login?to=" + $("#redirectAfter").text());
    }
}

$(document).ready(verifyToken);
