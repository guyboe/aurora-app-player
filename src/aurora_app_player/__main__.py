import os
import enum
import pathlib
from typing import Optional, Union

import typer
import pydantic

from benedict import benedict

from . import Plugin, Config


ENV = os.environ.get("ENV", "development")
STAGE = os.environ.get("STAGE", pathlib.Path.cwd().name)

config = Config(ENV, STAGE)

cli = typer.Typer()


class ConfigTypes(str, enum.Enum):
    yaml = "yaml"
    json = "json"
    ini = "ini"


class PlayTypes(str, enum.Enum):
    url = "url"
    path = "path"


@cli.command("config")
def _config(
    section: Optional[str] = typer.Option(None),
    format_: ConfigTypes = typer.Option(ConfigTypes.yaml, "--format"),
    output: Optional[pathlib.Path] = typer.Option(None),
    quiet: bool = typer.Option(False),
    indent: int = typer.Option(4)
):
    if output:
        output = output.open("w", encoding="utf-8")
    if section:
        d = benedict(config.dict()).get(section)
    else:
        d = benedict(config.dict(), keypath_separator=None)
    match format_:
        case "yaml":
            result = d.to_yaml(allow_unicode="utf-8", default_flow_style=False)
        case "json":
            result = d.to_json(ensure_ascii=False, indent=indent)
        case _:
            result = d.to_ini()
    if not quiet:
        print(result, file=output)


@cli.command("consume")
def _consume():
    plugin = Plugin(config)
    plugin.consume()


class UrlContainer(pydantic.BaseModel):
    url: Union[pydantic.FilePath, pydantic.AnyUrl]


@cli.command("play")
def _play(
    path: str, queue: config.Queues.Exchange.Name = typer.Option(None, help="play via queue")
):
    plugin = Plugin(config)
    if queue:
        url = UrlContainer(url=path).url
        if isinstance(url, pathlib.Path):
            print(f"Start playing {url.resolve()} via publishing bytes")
            with open(url, mode="r+b") as f:
                plugin.publish(f.read(), exchange=queue.value)
        else:
            print(f"Start playing {url} via url")
            plugin.publish(url, exchange=queue.value)
        return
    plugin.play(url)


if __name__ == "__main__":
    cli()
