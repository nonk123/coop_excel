const ws = new WebSocket(`ws://${window.location.host}/ws/`);

function respond(event, data) {
    ws.send(JSON.stringify({
        "e": event,
        "d": data
    }));
}

function update(data) {
    const excel = document.getElementById("excel");

    for (row of data.table) {
        const rowElement = document.createElement("tr");

        for (cell of row) {
            const dataElement = document.createElement("td");

            const valueElement = document.createElement("input");
            valueElement.style.width = "70px";
            valueElement.style.fontSize = "12px";
            valueElement.value = cell;

            dataElement.appendChild(valueElement);

            rowElement.appendChild(dataElement);
        }

        excel.appendChild(rowElement);
    }
}

const handlers = {
    "update": update
};

ws.onopen = function(e) {
    respond("connect", {
        "name": "Excel_Fan1001"
    })
}

ws.onmessage = function(e) {
    const response = JSON.parse(e.data);

    const event = response.e;

    if (event in handlers) {
        handlers[event](response.d);
    }
}
