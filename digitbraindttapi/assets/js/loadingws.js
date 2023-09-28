$(document).ready(function () {
    var dpserviceurl = "http://0.0.0.0:3000/"; //dttapi.cbp-routing.ch
    var solserviceurl = "http://0.0.0.0:3001/"; //dttapi.cbp-routing.ch
    var schserviceurl = "ws://0.0.0.0:3002/wslearn"; //dttapi.cbp-routing.ch

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
            'Access-Control-Allow-Origin': '*'
        }
    });
});

function Sleep(millisec) {
    return new Promise(resolve => setTimeout(resolve, millisec));
}