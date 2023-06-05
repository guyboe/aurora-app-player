import enum
from typing import Dict, List

import pydantic

import pydantic_config


class Config(pydantic_config.Settings):

    class Config:
        arbitrary_types_allowed = True

    class Queues(pydantic.BaseModel):

        class Config:
            use_enum_values = True
            arbitrary_types_allowed = True

        class Exchange(pydantic.BaseModel):

            class Config:
                use_enum_values = True

            class Name(pydantic_config.StrEnum):

                SAY = enum.auto()
                PLAY = enum.auto()
                EXECUTE = enum.auto()

            class Type(pydantic_config.StrEnum):
                TOPIC = enum.auto()
                FANOUT = enum.auto()

            name: str
            proxy: str
            type: Type = Type.TOPIC.value
            durable: bool = False

        class Queue(pydantic.BaseModel):
            name: str
            exchange: str
            routing_key: str = "*"
            durable: bool = False
            exclusive: bool = False
            auto_delete: bool = True
            priority: int = None
            callback: str

        url: pydantic.AmqpDsn
        exchanges: Dict[Exchange.Name, Exchange] = pydantic.Field(default_factory=dict)
        queues: List[Queue] = pydantic.Field(default_factory=list)

    queues: Queues = pydantic.Field(default_factory=Queues)
    storage: pydantic.DirectoryPath = "/tmp/aurora-plugin-player"
    player_command: str
    source: str
