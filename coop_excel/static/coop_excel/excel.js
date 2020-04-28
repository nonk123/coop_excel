const ws = new WebSocket(`ws://${window.location.host}/ws/`);

function respond(event, data) {
    ws.send(JSON.stringify({
        "e": event,
        "d": data
    }));
}

const statusElement = document.getElementById("status");

const handlers = {
    "authorized": function(data) {
        statusElement.style.color = data.color;
        statusElement.textContent = `I AM BECOME ${data.name}`;
    }
}

ws.onopen = function(e) {
    respond("connect", {
        "name": "Excel_Fan1001"
    })

    statusElement.textContent = "Authorizing...";
}

ws.onclose = e => statusElement.textContent = `Closed: ${e.code}`;

ws.onmessage = function(e) {
    const response = JSON.parse(e.data);

    const event = response.e;

    if (event in handlers) {
        handlers[event](response.d);
    }
}
