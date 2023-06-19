$(document).ready(function () {
    document.getElementById('btn-toggler').style.display = 'none';
    var nre = setInterval(fetchUpdatedData, 60000);
    function fetchUpdatedData() {
        $.ajax({
            url: "http://127.0.0.1:3002/getStatus",
            method: "GET",
            contentType: "application/json",
            crossDomain: true,
            success: function (res) {
                if (res.finished === "Done!") {
                    $("#data-container").html("Done!");
                    $("#data-container_1").html("Please vist: http://127.0.0.1:3002/machinetasks");
                    document.getElementById('btn-toggler').style.display = 'block';
                    clearInterval(nre);
                }
            },
            headers: {
                'Access-Control-Allow-Origin': '*'
            }
        });
    }
});