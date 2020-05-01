const ws = new WebSocket(`ws://${window.location.host}/ws/`);

ws.onclose = function(e) {
    console.log(`Connection closed: ${e.code}`);
}

function respond(event, data) {
    ws.send(JSON.stringify({
        e: event,
        d: data
    }));
}

let selection = {
    color: "gray",
    x: 0,
    y: 0,
    w: 1,
    h: 1
};

let selectedCells = [];

const inputElement = document.getElementById("input");

inputElement.onkeypress = function(e) {
    if (e.key == "Enter") {
        flushSetCells();
    }
}

function cellEdited(e) {
    if (selection) {
        inputElement.value = e.target.value;

        for (const cell of selectedCells) {
            cell.expression = e.target.value;
            cell.set();
        }
    }
}

inputElement.oninput = cellEdited;

const excel = document.getElementById("excel");

function range(x, y, w, h) {
    let ex = x + w;
    let ey = y + h;

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

function updateSelections(selections) {
    for (const row of excel.rows) {
        for (const td of row.cells) {
            td.children[0].selection = null;
        }
    }

    for (const selection of selections) {
        const selected = range(selection.x, selection.y, selection.w, selection.h);

        for (const cell of selected) {
            cell.selection = selection.color;
        }
    }

    redraw();
}

function updateSelection() {
    selectedCells = [];

    for (const cell of range(selection.x, selection.y, selection.w, selection.h)) {
        selectedCells.push(cell);
    }

    respond("update", {
        selection: selection
    });
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
        inputElement.value = editing.expression || editing.value;

        updateSelection();

        inputElement.focus();
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
                cells[i].expression = selectedCells[i].expression;
                cells[i].set();
            }

            flushSetCells();
        }
    }
}

let table = [];

function updateTable(delta) {
    for (cell of delta) {
        if (!table[cell.row]) {
            table[cell.row] = [];
        }

        table[cell.row][cell.col] = {
            expression: cell.expression,
            value: cell.value
        };
    }
}

let setCells = [];

function flushSetCells() {
    respond("set", {
        "cells": setCells
    });

    setCells = [];
}

function displayTable() {
    for (const [y, row] of table.entries()) {
        const rowElement = document.createElement("tr");

        for (const [x, cell] of row.entries()) {
            const td = document.createElement("td");

            const valueElement = document.createElement("input");
            valueElement.type = "text";
            valueElement.draggable = "true";
            valueElement.classList.add("cell");

            valueElement.value = cell.value;
            valueElement.expression = cell.expression;

            valueElement.x = x;
            valueElement.y = y;

            valueElement.row = y;
            valueElement.col = x;

            valueElement.set = function() {
                setCells.push({
                    row: y,
                    col: x,
                    expression: inputElement.value || valueElement.expression
                });
            };

            setListeners(valueElement);

            td.appendChild(valueElement);

            rowElement.appendChild(td);
        }

        excel.appendChild(rowElement);
    }

    selectedCells = [];

    if (excel.rows.length) {
        excel.rows[0].cells[0].children[0].focus();
    }
}

function redraw() {
    if (!excel.children.length) {
        displayTable();
    }

    for (const row in table) {
        for (const col in table[row]) {
            const cell = excel.rows[row].cells[col].children[0];

            if (cell.selection) {
                cell.style.background = cell.selection;
            } else {
                cell.style.background = "";
            }

            cell.value = table[row][col].value;
        }
    }
}

function update(data) {
    if (data.table) {
        updateTable(data.table);
        redraw();
    }

    if (data.selections) {
        updateSelections(data.selections);
    }
}

function authorized(data) {
    selection.color = data.color;
}

const handlers = {
    authorized: authorized,
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
