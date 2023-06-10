import pathlib
import logging
from subprocess import call
from functools import singledispatchmethod

import pydantic

from .config import Config
from .queues import Queues


class Plugin(Queues):

    NAME = "aurora_app_player"

    def __init__(self, config: Config):
        self.config = config
        super().__init__()

    def play(self, filename: str):
        call(self.config.player_command.format(filename).split(" "))

    @singledispatchmethod
    def _play(self, body, message):
        raise NotImplementedError(f"Unsupported type {type(body)}")

    @_play.register
    def _(self, body: bytes, message):
        logging.info("Playing bytes with hash %s", message.headers["v-hash"])
        filename = pathlib.Path(self.config.storage) / f"{message.headers['v-hash']}.wav"
        with open(filename, "wb") as f:
            f.write(body)
        self.play(filename)
        message.ack()

    @_play.register
    def _(self, body: pydantic.AnyUrl, message):
        logging.info("Playing url from %s", body)
        self.play(body)
        message.ack()
