const ws = new WebSocket(`ws://${window.location.host}/ws/`);

function respond(event, data) {
    ws.send(JSON.stringify({
        "e": event,
        "d": data
    }));
}

function update(data) {
    const excel = document.getElementById("excel");

    excel.textContent = "";

    for (const [y, row] of data.table.entries()) {
        const rowElement = document.createElement("tr");

        for (const [x, cell] of row.entries()) {
            const dataElement = document.createElement("td");

            const valueElement = document.createElement("input");
            valueElement.style.width = "70px";
            valueElement.style.fontSize = "12px";
            valueElement.value = cell;

            valueElement.oninput = () => {
                respond("set", {
                    "row": y,
                    "col": x,
                    "value": valueElement.value
                });
            };

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
