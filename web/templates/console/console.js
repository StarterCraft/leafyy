function prepare() {
    const selectTarget = $("#target")[0];
    if (selectTarget.options.length > 1) {
        selectTarget.selectedIndex = 1;
    }

    else { //доступен только сервер
        selectTarget.selectedIndex = 0;
    }

    onConsoleTargetSelected();

    $("select.log-level").each(
        (ix, sel) => {
            sel.style.color = $("select#" + sel.id).find("option[value=" + sel.value + "]").css("color");
        }
    )
}

window.onload = prepare;

function setStatus(content) {
    const status = $("#status")[0];
    status.innerHTML = content;

    const statusBar = $(".status-bar")[0];
    statusBar.style.display = "inherit";
}

function hideStatusBar() {
    $(".status-bar").hide();
}

function onLogLevelSelectChange(sel) {
    const thisSel = $("select#" + sel);
    thisSel.css(
        "color",
        thisSel.find("option[value=" + thisSel.val() + "]").css("color")
    )
}

let consoleAutoScroll = Boolean(getCookie("X10", true));
let consoleShouldUpdate = Boolean(getCookie("X11", true))
let minConsoleUpdatePeriod = Number(getCookie("X12", 2));
let maxConsoleUpdatePeriod = Number(getCookie("X13", 3600));

function onReceivedLogConfig(data) {
    const modal = ".modal#log-settings";
    const modalId = "log-settings";

    $("select#global", modal).val(data.level);
    $("#loggersBlacklist input:checkbox", modal).each(
        (ix, ckb) => ckb.checked = data.sources.filter(s => s.type == "logger")[ix].live
    );
    $("#loggersBlacklist select.log-level", modal).each(
        (ix, sel) => sel.value = data.sources.filter(s => s.type == "logger")[ix].mode
    );
    $("#devicesBlacklist input:checkbox", modal).each(
        (ix, ckb) => ckb.checked = data.sources.filter(s => s.type == "device")[ix].live
    );
    $("#devicesBlacklist select.decode-mode", modal).each(
        (ix, sel) => sel.value = data.sources.filter(s => s.type == "device")[ix].mode
    );
}

function onOpenSettings() {
    const modal = ".modal#log-settings";
    const modalId = "log-settings";

    $("#consoleAutoScroll", modal).prop("checked", consoleAutoScroll)
    $("#consoleShouldUpdate", modal).prop("checked", consoleShouldUpdate);
    $("#minConsoleUpdatePeriod", modal).val(minConsoleUpdatePeriod);
    $("#maxConsoleUpdatePeriod", modal).val(maxConsoleUpdatePeriod);

    $.getJSON("/log/config", null, onReceivedLogConfig);

    showModal(modalId);
}

function onSaveSettingsResult(status, data, settings) {
    if (status == 200) {
        setStatus(
            "<span class=\"positive bold\">" +
            "Настройки сохранены.</span>"
        )
    }
    else {
        setStatus(
            "<span class=\"negative bold\">" +
            "Не удалось сохранить:</span>" +
            data
        );
    }
}

function onSaveSettings() {
    const modal = ".modal#log-settings";
    const modalId = "log-settings";

    consoleAutoScroll = $("#consoleAutoScroll", modal).prop("checked");
    consoleShouldUpdate = $("#consoleShouldUpdate", modal).prop("checked");
    consoleUpdatePeriod = parseInt($("#minConsoleUpdatePeriod", modal).val());
    minConsoleUpdatePeriod = parseInt($("#minConsoleUpdatePeriod", modal).val());
    maxConsoleUpdatePeriod = parseInt($("#maxConsoleUpdatePeriod", modal).val());

    hideModal(modalId);

    Cookies.set("X10", consoleAutoScroll)
    Cookies.set("X11", consoleShouldUpdate)
    Cookies.set("X12", minConsoleUpdatePeriod);
    Cookies.set("X13", maxConsoleUpdatePeriod);

    var d = {};

    d.level = $("select#global", modal).val();
    d.sources = [];

    $("#loggersBlacklist input:checkbox", modal).each(
        (ix, ckb) => {
            d.sources.push({
                "name": ckb.id,
                "type": "logger",
                "mode": $("#loggersBlacklist select#" + ckb.id, modal).val(),
                "live": ckb.checked
            });
        }
    );

    $.ajax({
        type: "put",
        url: "/log/config",
        data: JSON.stringify(d)
    }).then(
        (data, textStatus, request) => onSaveSettingsResult(request.status, data, d),
        (request, textStatus, error) => onSaveSettingsResult(request.status, request.responseText, d)
    );
}

/** 
*    @param {string} content контент для размещения в новой строке консоли
*    @param {number} [index=1] 
*/
function addConsoleMessageLine(content) {
    const view = $("#view")[0];
    const lastLength = view.childElementCount / 2;

    var divLineNo = document.createElement("div");
    divLineNo.classList.add("log-lineno");
    divLineNo.textContent = lastLength + 1;
    view.appendChild(divLineNo);

    var divLine = document.createElement("div");
    divLine.classList.add("log-message");
    divLine.innerHTML = content;
    view.appendChild(divLine);

    if (consoleAutoScroll) 
        view.scrollTop = view.scrollHeight;
}

function dataTypeToRegex(type) {
    var expression = "";

    switch (type) {
        case "ascii":
            expression = "[ a-zA-Z0-9,;()!?-]+";
            break;

        case "bin":
            expression = "((0b|0B|b|B)[01]{1,8}[ ]*)+";
            break;

        case "oct":
            expression = "((0o|0O|o|O)[0-7]{1,8}[ ]*)+";
            break;

        case "dec":
            expression = "(\d{1,3}[ ]*)+";
            break;

        case "hex":
            expression = "((0x|0X|x|X)[0-9a-fA-F]{1,2}[ ]*)+";
            break;

        default:
            expression = "[a-zA-Z0-9,;()!?-]+";
            break;
    }

    return expression;
}

function onSetUpdatePeriod() {
    // not implemented yet
}

function onConsoleInputKeyDown(event) {
    switch (event.key) {
        case "Enter":
            onConsoleSend();
            break;

        default:
            break;
    }
}

function onConsoleTargetSelected() {
    const selectTarget = $("#target")[0];
    const target = selectTarget.options[selectTarget.selectedIndex].value;

    if (target == "server") {
        var selectType = $("#type");
        selectType.val("ascii");
        selectType.addClass("hidden");
    }

    else {
        var selectType = $("#type");
        selectType.val("ascii");
        selectType.removeClass("hidden");
    }

    onConsoleInputTypeSelected();
}

function onConsoleInputTypeSelected() {
    const inputData = $("#data")[0];
    const selectType = $("#type")[0];
    const type = selectType.options[selectType.selectedIndex].value;

    inputData.pattern = dataTypeToRegex(type);
}

let lastConsoleUpdateResult = false;

function onReceivedUpdatedConsoleData(data) {
    data.forEach(addConsoleMessageLine);
    lastConsoleUpdateResult = (data.length > 0);
}

function onUpdateConsoleData() {
    $.get("/log/update", data => {
        onReceivedUpdatedConsoleData(data);
    });
}

let consoleUpdatePeriod = minConsoleUpdatePeriod;
let consoleUpdateIntervalId = null;

function onManualUpdateConsoleData() {
    console.debug('Conssole updated manually, setting period to minimum period', minConsoleUpdatePeriod);
    consoleUpdatePeriod = minConsoleUpdatePeriod;
    onUpdateConsoleData();
}

function keepConsoleUpdated() {
    onUpdateConsoleData();

    console.debug("Periodic update " + (lastConsoleUpdateResult ? "done " : "failed: empty ") +
        "with period of " + consoleUpdatePeriod + " (range " + minConsoleUpdatePeriod + "..." + maxConsoleUpdatePeriod + ")"
    );

    if (!lastConsoleUpdateResult && consoleUpdatePeriod < maxConsoleUpdatePeriod && consoleUpdatePeriod * 2 <= maxConsoleUpdatePeriod) {
        window.clearInterval(consoleUpdateIntervalId);
        consoleUpdatePeriod *= 2;
        consoleUpdateIntervalId = window.setInterval(keepConsoleUpdated, consoleUpdatePeriod * 1000);
        console.debug("Periodic update period increases: no update messages. Set period to " + consoleUpdatePeriod);
        return;
    }

    if (lastConsoleUpdateResult && consoleUpdatePeriod > minConsoleUpdatePeriod) {
        consoleUpdatePeriod = minConsoleUpdatePeriod;
        window.clearInterval(consoleUpdateIntervalId);
        consoleUpdateIntervalId = window.setInterval(keepConsoleUpdated, consoleUpdatePeriod * 1000);
        console.debug("Periodic update period set to minimum: update messages detected. Set period to " + consoleUpdatePeriod);
        return;
    }
}

onUpdateConsoleData();
consoleUpdateIntervalId = window.setInterval(keepConsoleUpdated, consoleUpdatePeriod * 1000);

function onConsoleSendResult(status, responseText, message) {
    if (status == 202) {
        report(
            "INFO",
            "USER_IP >> " + message.target + " [Accepted] " + message.data
        );

        const inputData = $("#data")[0];
        inputData.value = "";
    }

    else {
        report(
            "ERROR",
            "USER_IP >> " + message.target + " [Failure (" + status + ", " + responseText + ")] " + message.data
        );
    }

    onUpdateConsoleData();
}

function fetchConsoleForm() {
    var selectTarget = $("#target")[0];
    var target = selectTarget.options[selectTarget.selectedIndex].value;

    var inputData = $("#data")[0];
    var data = inputData.value.trim();

    var selectType = $("#type")[0];
    var type = selectType.options[selectType.selectedIndex].value;

    var d = {
        "target": target,
        "data": data,
        "type": type
    };

    return d;
}

function onConsoleSend() {
    var d = fetchConsoleForm();
    var re = new RegExp(dataTypeToRegex(d.type), "u")

    if (!d.data) {
        setStatus(
            "<span class=\"negative bold\">" +
            "Не удалось отправить:</span>" +
            " нет текста сообщения."
        );
        return;
    }

    if (!re.test(d.data)) {
        setStatus(
            "<span class=\"negative bold\">" +
            "Не удалось отправить:</span> " +
            "сообщение не соответствует формату " + d.type.toUpperCase() + "."
        );
        return;
    }

    $.ajax({
        type: "post",
        url: "/console",
        data: JSON.stringify(d)
    }).then(
        (data, textStatus, request) => onConsoleSendResult(request.status, data, d),
        (request, textStatus, error) => onConsoleSendResult(request.status, request.responseText, d)
    );
}
