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

function prepare() {
    //$("#loginForm").on("submit", login);
}

$(document).ready(prepare);
