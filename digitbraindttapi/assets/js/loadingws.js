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
                            ws.onmessage = async function (event) {
                                data = JSON.parse(event.data);

                                const eleStat = document.getElementById("data-container");
                                eleStat.innerHTML = data.message;

                                const eleTime = document.getElementById("data-container_1");
                                eleTime.innerHTML = `Time Lapsed: ${data.time}`;

                                const eleComMac = document.getElementById("data-container_2");
                                eleComMac.innerHTML = `Completed Machines: ${data.completedMac}/${data.totalMac}`;

                                if (data.message === "Done") {
                                    await Sleep(3000);
                                    window.location.replace("http://127.0.0.1:3006/getexistingsolution");
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
});

function Sleep(millisec) {
    return new Promise(resolve => setTimeout(resolve, millisec));
}