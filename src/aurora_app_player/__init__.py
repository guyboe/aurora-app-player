import atexit
import pathlib
import logging
import subprocess
from contextlib import suppress
from functools import singledispatchmethod
from typing import Dict, Literal, Any

import pydantic

from .config import Config
from .queues import Queues


class Plugin(Queues):

    NAME = "aurora_app_player"

    processes: Dict[int, Any] = {}

    def __init__(self, config: Config):
        self.config = config
        super().__init__()

    def play(self, filename: str):
        command = self.config.player_command.format(filename)
        # pylint: disable=consider-using-with
        process = subprocess.Popen(
            command.split(" "),
            stdin=subprocess.PIPE,
            start_new_session=True,
            text=True
        )
        self.processes[process.pid] = process
        atexit.register(self.terminate, process.pid)
        logging.info("Process %d [%s] has been started", process.pid, command)

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

    def _execute(self, body, message):

        class Execute(pydantic.BaseModel):
            name: Literal["play"]
            action: Literal["stop"]
            value: int = None

        with suppress(pydantic.ValidationError):
            execute = Execute.parse_obj(body)
            logging.info("Got command %s for execute", execute)
            processes = [k for k in self.processes if k == execute.value or not execute.value]
            for pid in processes:
                self.terminate(pid)
            if not processes:
                logging.debug("Doesn't have proceesses to terminate")

        message.ack()

    def terminate(self, pid):
        if pid not in self.processes:
            return
        self.processes[pid].terminate()
        logging.debug(
            "Process %d has been terminated with status %d", pid, self.processes[pid].wait()
        )
        del self.processes[pid]
