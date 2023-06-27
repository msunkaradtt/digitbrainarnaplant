$(document).ready(function () {
    $.ajax({
        url: "http://127.0.0.1:3000/",
        method: "GET",
        contentType: "application/json",
        crossDomain: true,
        success: function (res) {
            if (res.message === "Done") {
                $.ajax({
                    url: "http://127.0.0.1:3001/",
                    method: "GET",
                    contentType: "application/json",
                    crossDomain: true,
                    success: function (res) {
                        if (res.message === "Done") {
                            var ws = new WebSocket("ws://127.0.0.1:3002/wslearn");
                            ws.onmessage = function (event) {
                                data = JSON.parse(event.data);
                                if (data.message === "Done") {
                                    window.location.replace("http://127.0.0.1:3006/getexistingsolution")
                                }
                            }
                        }
                    },
                    headers: {
                        'Access-Control-Allow-Origin': '*'
                    }
                });
            }
        },
        headers: {
            'Access-Control-Allow-Origin': '*'
        }
    });
    /*var ws = new WebSocket("ws://127.0.0.1:3002/wslearn");
    ws.onmessage = function (event) {
        console.log(event.data)
    }*/
});