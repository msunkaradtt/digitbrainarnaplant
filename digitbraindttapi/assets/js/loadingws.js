$(document).ready(function () {
    var dpserviceurl = "http://localhost:3000/";
    var solserviceurl = "http://localhost:3001/";
    var schserviceurl = "ws://localhost:3002/wslearn";

    $.ajax({
        url: dpserviceurl,
        method: "GET",
        contentType: 'application/json',
        crossDomain: true,
        success: function (res) {
            if (res.message === "Done") {
                $.ajax({
                    url: solserviceurl,
                    method: "GET",
                    contentType: "application/json",
                    crossDomain: true,
                    success: function (res) {
                        if (res.message === "Done") {
                            var ws = new WebSocket(schserviceurl);
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
                                    window.location.replace("/getexistingsolution");
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
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': true
        }
    });
});

function Sleep(millisec) {
    return new Promise(resolve => setTimeout(resolve, millisec));
}