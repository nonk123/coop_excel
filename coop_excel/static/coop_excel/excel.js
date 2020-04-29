const ws = new WebSocket(`ws://${window.location.host}/ws/`);

function respond(event, data) {
    ws.send(JSON.stringify({
        e: event,
        d: data
    }));
}

let editing = null;

const inputElement = document.getElementById("input");

inputElement.oninput = e => {
    if (editing) {
        editing.value = e.target.value;
    }
}

function update(data) {
    const excel = document.getElementById("excel");
    excel.textContent = "";

    for (const [y, row] of data.table.entries()) {
        const rowElement = document.createElement("tr");

        for (const [x, cellValue] of row.entries()) {
            const dataElement = document.createElement("td");

            const valueElement = document.createElement("input");
            valueElement.type = "text";
            valueElement.style.width = "70px";
            valueElement.style.height = "17px";
            valueElement.style.fontSize = "12px";
            valueElement.value = cellValue;

            valueElement.oninput = function (e) {
                inputElement.value = e.target.value;

                respond("set", {
                    row: y,
                    col: x,
                    value: e.target.value
                });
            };

            valueElement.onfocus = function (e) {
                if (editing) {
                    editing.classList.remove("selected");
                }

                editing = e.target;
                inputElement.value = editing.value;

                editing.classList.add("selected");
            };

            dataElement.appendChild(valueElement);

            rowElement.appendChild(dataElement);
        }

        excel.appendChild(rowElement);
    }
}

const handlers = {
    update: update
};

ws.onopen = function(e) {
    respond("connect", {
        name: "Excel_Fan1001"
    })
}

ws.onmessage = function(e) {
    const response = JSON.parse(e.data);

    const event = response.e;

    if (event in handlers) {
        handlers[event](response.d);
    }
}
