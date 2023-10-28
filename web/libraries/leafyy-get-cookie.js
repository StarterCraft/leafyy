function getCookie(id, _default) {
    c = Cookies.get(id);
    if (typeof c === "undefined")
        return _default;

    else return c;
}
