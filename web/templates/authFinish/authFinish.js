function finishLogout()
{
    var ACCESS = $("#X00").text();
    var REFRESH = $("#X01").text();

    Cookies.set("X00", ACCESS);
    Cookies.set("X01", REFRESH);

    $("#X00").remove();
    $("#X01").remove();

    window.location.href = ($("#redirectAfter").text());
}

$(document).ready(finishLogout);
