if (typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function()
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

function prepareIt() {
    if ($(document).height() > $(window).height()) {
        $("footer").removeClass("fixed-bottom");
    }

    $(document).prop("title", $("body title").text());
}

$(document).ready(prepareIt);

function setStatus(content) {
    const status = $("#status")[0];
    status.innerHTML = content;

    const statusBar = $(".status-bar")[0];
    statusBar.style.display = "inherit";
}

function hideStatusBar() {
    $(".status-bar").hide();
}

function getCookie(id, _default) {
    c = Cookies.get(id);
    if (typeof c === "undefined")
        return _default;

    else return c;
}

function toggleModal(modalId) {
    if ($(".modal#" + modalId).is(":visible")) {
        hideModal(modalId);
    }

    else {
        showModal(modalId);
    }
}

function showModal(modalId) {
    $(".modal-field").css("display", "flex");
    $(".modal#" + modalId).css("display", "flex");
}

function hideModal(modalId) {
    $(".modal#" + modalId).css("display", "none");
    $(".modal-field").css("display", "none");
}

function toggleCheckbox(boxId) {
    $("input#" + boxId).prop("checked", !$("input#" + boxId).prop("checked"));
}

$.ajaxSetup({
    processData: false,
    contentType: "application/json",
    headers: {"Authorization": "Bearer " + getCookie("X00", null)}
})

function reportStdCallback(request) {
    if (request.status > 299)
        console.warn(request.responseText);
}

function report(level, message, callback = reportStdCallback) {
    const levels = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    ];

    level = level.toUpperCase();
    if (!levels.includes(level)){
        throw SyntaxError("Unsupported level: " + level);
    }

    $.ajax({
        url: "/log/",
        type: "POST",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({
            "time": Date.now(),
            "level": level,
            "message": message
        }),
        success: data => {
            callback(data);
        },
        error: request => {
            console.warn(request.responseText);
        }
    });
}
