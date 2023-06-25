function onSearchQuery() {
    const query = $("#search").val();

    if (query) {
        $("#view .file-card").each(
            (ix, crd) => {
                const name = crd.textContent.trim();
                if (!name.includes(query))
                    crd.style.display = "none";
                else
                    crd.style.display = "flex";
            }
        );
    }

    if (!query) {
        $("#view").show();
        $("#view .file-card").show();
    }

    if ($("#view .file-card:visible").length) {
        $("#view").show();
        $("#no-content").hide();
    }

    else {
        $("#view").hide();
        $("#no-content").show();
    }
}
