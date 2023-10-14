function finishLogin()
{
    var ACCESS = $("#X00").text();
    var REFRESH = $("#X01").text();

    Cookies.set("X00", ACCESS);
    Cookies.set("X01", REFRESH);

    $("#X00").remove();
    $("#X01").remove();

    window.location = $("#redirectAfter").text();
}

$(document).ready(finishLogin);
