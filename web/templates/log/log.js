function prepare() {
    const selectTarget = $("#target")[0];
    if (selectTarget.options.length > 1) {
        selectTarget.selectedIndex = 1;
    }

    else { //доступен только сервер
        selectTarget.selectedIndex = 0;
    }

    onConsoleTargetSelected();
}

window.onload = prepare;

function setStatus(content) {
    const status = $("#status")[0];
    status.innerHTML = content;

    const statusBar = $("#statusBar")[0];
    statusBar.style.display = "inherit";
}

function hideStatusBar() {
    $("#statusBar").hide();
}

let consoleShouldUpdate = getCookie("X01", true)
let minConsoleUpdatePeriod = getCookie("X02", 2);
let maxConsoleUpdatePeriod = getCookie("X03", 3600);

function onOpenSettings() {
    const modal = ".modal#log-settings";
    const modalId = "log-settings";

    $("#consoleShouldUpdate", modal).prop("checked", consoleShouldUpdate);
    $("#minConsoleUpdatePeriod", modal).val(minConsoleUpdatePeriod);
    $("#maxConsoleUpdatePeriod", modal).val(maxConsoleUpdatePeriod);
    
    showModal(modalId);
}

function onSaveSettings() {
    const modal = ".modal#log-settings";
    const modalId = "log-settings";

    consoleShouldUpdate = $("#consoleShouldUpdate", modal).prop("checked");
    minConsoleUpdatePeriod = $("#minConsoleUpdatePeriod", modal).val();
    maxConsoleUpdatePeriod = $("#maxConsoleUpdatePeriod", modal).val();

    hideModal(modalId);

    Cookies.set("X01", consoleShouldUpdate)
    Cookies.set("X02", minConsoleUpdatePeriod);
    Cookies.set("X03", maxConsoleUpdatePeriod);
}

/** 
*    @param {string} content контент для размещения в новой строке консоли
*    @param {number} [index=1] 
*/
function addConsoleMessageLine(content, index = 1) {
    const view = $("#view")[0];
    const lastLength = view.childElementCount / 2;

    var divLineNo = document.createElement("div");
    divLineNo.classList.add("log-lineno");
    divLineNo.textContent = index + lastLength;
    view.appendChild(divLineNo);

    var divLine = document.createElement("div");
    divLine.classList.add("log-message");
    divLine.innerHTML = content;
    view.appendChild(divLine);
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
            expression = "((0x|0X|x|X)[0-9a-f]{1,2}[ ]*)+";
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
        var selectType = $("#type")[0];
        selectType.value = "ascii";
        selectType.classList.add("hidden");
    }

    else {
        var selectType = $("#type")[0];
        selectType.value = "ascii";
        selectType.classList.remove("hidden");
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
    $.get("/log/update",
        function (data, textStatus, jqXHR) {
            onReceivedUpdatedConsoleData(data);
        },
        
    );
}

let consoleUpdatePeriod = 2;
let consoleUpdateIntervalId = null;

function keepConsoleUpdated() {
    onUpdateConsoleData();

    console.debug("Periodic update " + (lastConsoleUpdateResult ? "done " : "failed: empty ") + 
        "with period of " + consoleUpdatePeriod + " (range " + minConsoleUpdatePeriod + "..." + maxConsoleUpdatePeriod + ")"
    );

    if (!lastConsoleUpdateResult && consoleUpdatePeriod < maxConsoleUpdatePeriod) {
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

consoleUpdateIntervalId = window.setInterval(keepConsoleUpdated, consoleUpdatePeriod)

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
    var re =  new RegExp(dataTypeToRegex(d.type), "u")

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
            "сообщение не соответствует формату "+ d.type.toUpperCase() + "."
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
