function addConsoleMessageLine(content, index) {
    const view = document.getElementById("view");

    var divLineNo = document.createElement("div");
    divLineNo.classList.add("log-lineno");
    divLineNo.textContent = index;
    view.appendChild(divLineNo);

    var divLine = document.createElement("div");
    divLine.classList.add("log-message");
    divLine.innerHTML = content;
    view.appendChild(divLine);
}

function onReceivedUpdatedConsoleData(data) {
    var array = JSON.parse(data);

    array.forEach(addConsoleMessageLine);
}

function onUpdateConsoleData() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            onReceivedUpdatedConsoleData(xmlHttp.responseText)
    };
    xmlHttp.open("GET", "/log/update", true); // true for asynchronous
    xmlHttp.send(null);
}

function fetchConsoleForm() {
    var d = new FormData(document.getElementById("console"),
    document.getElementById("consoleSend"));
    console.warn(d);
    return d;
}

function handleForm(event) {
    event.preventDefault();
}

function onConsoleSend() {
    var xmlHttp = new XMLHttpRequest();

    xmlHttp.open("POST", "/console", true); // true for asynchronous

    // Send the proper header information along with the request
    xmlHttp.setRequestHeader("Content-Type", "multipart/form-data");

    xmlHttp.send(fetchConsoleForm());
}
