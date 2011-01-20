class Messenger:

    def __init__(self):
        self.callbacks = {}

    def send(self, type, message):
        for callback in self.callbacks[type]:
            callback(message)

    def subscribe(self, type, callback):
        if type not in self.callbacks:
            self.callbacks[type] = []

        self.callbacks[type].append(callback)
