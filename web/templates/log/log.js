function setStatus(content) {
    const status = document.getElementById("status");
    status.innerHTML = content;

    const statusBar = document.getElementById("statusBar");
    statusBar.style.display = "inherit";
}

function hideStatusBar() {
    const statusBar = document.getElementById("statusBar");
    statusBar.style.display = "none";
}

/** 
*    @param {string} content контент для размещения в новой строке консоли
*    @param {number} [index=1] 
*/
function addConsoleMessageLine(content, index = 1) {
    const view = document.getElementById("view");
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

function prepare() {
    const selectTarget = document.getElementById("target");
    if (selectTarget.options.length > 1) {
        selectTarget.selectedIndex = 1;
    }

    else { //доступен только сервер
        selectTarget.selectedIndex = 0;
    }

    onConsoleTargetSelected();
}

window.onload = prepare;

function dataTypeToRegex(type) {
    var expression = "";
    
    switch (type) {
        case "ascii":
            expression = "[a-zA-Z0-9 \\-,;()]+";
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
            expression = "[a-zA-Z0-9 \\-,;()]+";
            break;
    }

    return expression;
}

function onSetUpdatePeriod() {
    // not implemented yet
}

function onConsoleTargetSelected() {
    const selectTarget = document.getElementById("target");
    const target = selectTarget.options[selectTarget.selectedIndex].value;

    if (target == "server") {
        var selectType = document.getElementById("type");
        selectType.value = "ascii";
        selectType.classList.add("hidden");
    }

    else {
        var selectType = document.getElementById("type");
        selectType.value = "ascii";
        selectType.classList.remove("hidden");
    }

    onConsoleInputTypeSelected();
}

function onConsoleInputTypeSelected() {
    const inputData = document.getElementById("data");
    const selectType = document.getElementById("type");
    const type = selectType.options[selectType.selectedIndex].value;
    
    inputData.pattern = dataTypeToRegex(type);
}

function onReceivedUpdatedConsoleData(data) {
    var array = JSON.parse(data);

    array.forEach(addConsoleMessageLine);
}

function onUpdateConsoleData() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            onReceivedUpdatedConsoleData(xmlHttp.responseText)
    };
    xmlHttp.open("GET", "/log/update", true); // true for asynchronous
    xmlHttp.send(null);
}

function onConsoleSendResult(status, responseText, message) {
    if (status == 202) {
        report(
            "INFO", 
            "Console >> " + message.target + " [Accepted] " + message.data
        );
    }

    else {
        report(
            "ERROR", 
            "Console >> " + message.target + " [Failure (" + status + ", " + responseText + ")] " + message.data
        );
    }

    onUpdateConsoleData();
}

function fetchConsoleForm() {
    var selectTarget = document.getElementById("target");
    var target = selectTarget.options[selectTarget.selectedIndex].value;

    var inputData = document.getElementById("data");
    var data = inputData.value;

    var selectType = document.getElementById("type");
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

    var xmlHttp = new XMLHttpRequest();

    xmlHttp.onreadystatechange = () => {
        if (xmlHttp.readyState == 4) {
            onConsoleSendResult(
                xmlHttp.status, 
                (xmlHttp.responseText ? xmlHttp.responseText : "none"),
                d);
        }
    };

    xmlHttp.open("POST", "/console", true); // true for asynchronous

    // Send the proper header information along with the request
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    xmlHttp.send(JSON.stringify(d));
}
