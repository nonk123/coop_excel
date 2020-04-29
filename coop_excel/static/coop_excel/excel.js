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

function range(x, y, w, h) {
    let ex = x + selection.w;
    let ey = y + selection.h;

    if (ex < x) {
        [ex, x] = [x, ex];
    }

    ex++;

    if (ey < y) {
        [ey, y] = [y, ey];
    }

    ey++;

    const range = [];

    for (const row of [...excel.rows].slice(y, ey)) {
        for (const td of [...row.cells].slice(x, ex)) {
            range.push(td.children[0]);
        }
    }

    return range;
}

function updateSelection() {
    for (const cell of selectedCells) {
        cell.classList.remove("selected");
    }

    selectedCells = [];

    for (const cell of range(selection.x, selection.y, selection.w, selection.h)) {
        selectedCells.push(cell);
    }

    for (const cell of selectedCells) {
        cell.classList.add("selected");
    }
}

document.ondragover = function(e) {
    e.preventDefault();
}

let dragging = null;

function setListeners(elt) {
    elt.oninput = cellEdited;

    elt.onmousedown = function(e) {
        if (e.shiftKey) {
            selection.w = e.target.x - selection.x;
            selection.h = e.target.y - selection.y;

            updateSelection();

            e.preventDefault();
        }
    };

    elt.onfocus = function(e) {
        selection.x = e.target.x;
        selection.y = e.target.y;

        selection.w = 0;
        selection.h = 0;

        editing = e.target;
        inputElement.value = editing.value;

        updateSelection();
    };

    elt.ondrag = function(e) {
        dragging = e.target;
    };

    elt.ondragend = function(e) {
        dragging = null;
    }

    elt.ondrop = function(e) {
        if (dragging) {
            const cells = range(e.target.x, e.target.y, selection.w, selection.h);

            for (const i in cells) {
                cells[i].value = selectedCells[i].value;
            }
        }
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
            valueElement.draggable = "true";
            valueElement.style.width = "70px";
            valueElement.style.height = "17px";
            valueElement.style.fontSize = "12px";
            valueElement.value = cellValue;

            valueElement.x = x;
            valueElement.y = y;

            valueElement.row = y;
            valueElement.col = x;

            valueElement.set = function() {
                respond("set", {
                    row: y,
                    col: x,
                    value: valueElement.value
                });
            };

            setListeners(valueElement);

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
