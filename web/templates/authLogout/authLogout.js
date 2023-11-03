function finishLogout()
{
    Cookies.set("X00", "");
    Cookies.set("X01", "");

    window.location.href = "/auth/login";
}

$(document).ready(finishLogout);
