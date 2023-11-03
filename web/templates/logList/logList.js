function onDownloadLog(file) {
    var logText = '';

    $.ajax({
        type: "GET",
        url: "/log/" + file,
        success: r => logText = r,
        error: e => alert(e)
    });

    saveTextAs(logText, file);
}

function onSearchQuery() {
    console.debug("onInput Raised!");

    const query = $("#search").val();

    if (query) {
        console.info("query non-void, query", query);

        $("#view .file-card").each(
            (ix, crd) => {
                const name = crd.textContent.trim();
                //console.debug("Dispatching card", ix, "with content", name, "q", query, "condition:", !name.includes(query) ? " not eligible" : "ELIGIBLE")

                if (!name.includes(query))
                    crd.style.display = "none";
                else {
                    crd.style.display = "flex"; console.log("SHOW CARD", ix, name)
                }
            }
        );
    }

    else {
        console.warn("query void, showing all cards");

        $("#view").show();
        $("#view .file-card").show();
    }

    if ($("#view .file-card:visible").length) {
        console.info("cards visible, hiding void msg");

        $("#view").show();
        $("#no-content").hide();
    }

    else {
        console.warn("no cards visible, showing void msg");

        $("#view").hide();
        $("#no-content").show();
    }
}
