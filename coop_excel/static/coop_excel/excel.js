const ws = new WebSocket(`ws://${window.location.host}/ws/`);

function respond(event, data) {
    ws.send(JSON.stringify({
        e: event,
        d: data
    }));
}

let selection = {
    x: 0,
    y: 0,
    w: 1,
    h: 1
};

let selectedCells = [];

const inputElement = document.getElementById("input");

function cellEdited(e) {
    if (selection) {
        inputElement.value = e.target.value;

        for (const cell of selectedCells) {
            cell.value = e.target.value;
            cell.set();
        }
    }
}

inputElement.oninput = cellEdited;

const excel = document.getElementById("excel");

function updateSelection() {
    for (const cell of selectedCells) {
        cell.classList.remove("selected");
    }

    selectedCells = [];

    let bx = selection.x;
    let by = selection.y;

    let ex = bx + selection.w;
    let ey = by + selection.h;

    if (ex < bx) {
        [ex, bx] = [bx, ex];
    }

    ex++;

    if (ey < by) {
        [ey, by] = [by, ey];
    }

    ey++;

    for (const row of [...excel.rows].slice(by, ey)) {
        for (const td of [...row.cells].slice(bx, ex)) {
            selectedCells.push(td.children[0]);
        }
    }

    for (const cell of selectedCells) {
        cell.classList.add("selected");
    }
}

function redraw(table) {
    excel.textContent = "";

    for (const [y, row] of table.entries()) {
        const rowElement = document.createElement("tr");

        for (const [x, cellValue] of row.entries()) {
            const dataElement = document.createElement("td");

            const valueElement = document.createElement("input");
            valueElement.type = "text";
            valueElement.style.width = "70px";
            valueElement.style.height = "17px";
            valueElement.style.fontSize = "12px";
            valueElement.value = cellValue;

            valueElement.x = x;
            valueElement.y = y;

            valueElement.row = y;
            valueElement.col = x;

            valueElement.set = function () {
                respond("set", {
                    row: y,
                    col: x,
                    value: valueElement.value
                });
            }

            valueElement.oninput = cellEdited;

            valueElement.onmousedown = function(e) {
                if (e.shiftKey) {
                    selection.w = e.target.x - selection.x;
                    selection.h = e.target.y - selection.y;

                    updateSelection();

                    e.preventDefault();
                }
            }

            valueElement.onfocus = function (e) {
                selection.x = x;
                selection.y = y;

                selection.w = 0;
                selection.h = 0;

                editing = e.target;
                inputElement.value = editing.value;

                updateSelection();
            };

            dataElement.appendChild(valueElement);

            rowElement.appendChild(dataElement);

            excel.appendChild(rowElement);
        }
    }
}

function applyDelta(delta) {
    excel.rows[delta.row].cells[delta.col].children[0].value = delta.value;
}

function update(data) {
    if (data.table) {
        redraw(data.table);
    }

    if (data.delta && excel.children.length) {
        applyDelta(data.delta);
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
