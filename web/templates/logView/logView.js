function onReceivedLog(file, response) {
    alert(response);
    saveTextAs(response, file);
}

function onDownloadLog(file) {
    var logText = '';

    $.ajax({
        type: "GET",
        url: "/log/" + file,
        success: r => onReceivedLog(file, r),
        error: e => alert(e)
    });
}
