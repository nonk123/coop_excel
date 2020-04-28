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
            "set": self.set
        }

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
            "table": table.values
        })

    def connected(self, data):
        if "name" not in data:
            self.close(self.INVALID_PAYLOAD)

        self.name = data["name"]
        self.color = self.COLORS[(len(self.players) - 1) % len(self.COLORS)]

        self.send_event("authorized", {
            "name": self.name,
            "color": self.color
        })

        self.update()

    def set(self, data):
        if "row" not in data or "col" not in data or "value" not in data:
            self.close(self.INVALID_PAYLOAD)

        table.set(int(data["row"]), int(data["col"]), data["value"])

        for player in self.players:
            if player is not self:
                player.update()

    def receive(self, text_data):
        message = json.loads(text_data)

        event = message["e"]

        if event in self.handlers:
            self.handlers[event](message["d"])
        else:
            self.close(self.INVALID_PAYLOAD)
