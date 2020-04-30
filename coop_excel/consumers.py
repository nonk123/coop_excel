from channels.generic.websocket import WebsocketConsumer

import json

from .excel import table

class ExcelConsumer(WebsocketConsumer):
    INVALID_PAYLOAD = 4004

    COLORS = ("red", "green", "blue", "yellow", "cyan", "magenta", "saddlebrown", "gray")

    players = []

    def connect(self):
        self.handlers = {
            "connect": self.connected,
            "update": self.updated,
            "set": self.set
        }

        self.selection = {}

        self.accept()

        self.players.append(self)

    def disconnect(self, close_code):
        self.players.remove(self)

    def send_event(self, event, data):
        self.send(json.dumps({
            "e": event,
            "d": data
        }, default=lambda x: x.__dict__))

    def update(self):
        self.send_event("update", {
            "table": table.networked,
            "selections": self.selections
        })

    def delta(self, row, col, expr, value):
        self.send_event("update", {
            "delta": {
                "row": row,
                "col": col,
                "value": value,
                "expression": expr
            }
        })

    def connected(self, data):
        if "name" not in data:
            return self.close(self.INVALID_PAYLOAD)

        self.name = data["name"]
        self.color = self.COLORS[(len(self.players) - 1) % len(self.COLORS)]

        self.send_event("authorized", {
            "name": self.name,
            "color": self.color
        })

        self.update()

    def set(self, data):
        if "row" not in data or "col" not in data or "expression" not in data:
            return self.close(self.INVALID_PAYLOAD)

        row, col = int(data["row"]), int(data["col"])
        e, v = table.set(row, col, data["expression"])

        for player in self.players:
            player.delta(row, col, e, v)

    @property
    def selections(self):
        return [other.selection for other in self.players if other.selection]

    def updated(self, data):
        if "selection" in data:
            self.selection = data["selection"]

            for player in self.players:
                player.send_event("update", {
                    "selections": self.selections
                })

    def receive(self, text_data):
        message = json.loads(text_data)

        event = message["e"]

        if event in self.handlers:
            self.handlers[event](message["d"])
        else:
            self.close(self.INVALID_PAYLOAD)
