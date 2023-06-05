import pathlib
import logging
from subprocess import call

from .config import Config
from .queues import Queues


class Plugin(Queues):

    NAME = "aurora_app_player"

    def __init__(self, config: Config):
        self.config = config
        super().__init__()

    def play(self, filename: str):
        call(self.config.player_command.format(filename).split(" "))

    def _play(self, body, message):
        filename = pathlib.Path(self.config.storage) / f"{message.headers['v-hash']}.wav"
        with open(filename, "wb") as f:
            f.write(body)
        self.play(filename)
        message.ack()
