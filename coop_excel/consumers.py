from channels.generic.websocket import WebsocketConsumer

import json
import copy

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

    def update(self, **kwargs):
        data = {
            "selections": self.selections
        }

        if "delta" in kwargs:
            data["table"] = kwargs["delta"]

        self.send_event("update", data)

    def connected(self, data):
        if "name" not in data:
            return self.close(self.INVALID_PAYLOAD)

        self.name = data["name"]
        self.color = self.COLORS[(len(self.players) - 1) % len(self.COLORS)]

        self.send_event("authorized", {
            "name": self.name,
            "color": self.color
        })

        self.update(delta=table.delta([]))

    def set(self, data):
        if "cells" not in data:
            return self.close(self.INVALID_PAYLOAD)

        table.update_with_stripped(data["cells"])

        delta = table.delta()

        for player in self.players:
            player.update(delta=delta)

    @property
    def selections(self):
        return [other.selection for other in self.players if other.selection]

    def updated(self, data):
        if "selection" in data:
            self.selection = data["selection"]

            for player in self.players:
                player.update()

    def receive(self, text_data):
        message = json.loads(text_data)

        event = message["e"]

        if event in self.handlers:
            self.handlers[event](message["d"])
        else:
            self.close(self.INVALID_PAYLOAD)
