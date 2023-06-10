import os
import enum
import pathlib
from typing import Optional

import typer
from pydantic import BaseModel, AnyUrl

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


class UrlContainer(BaseModel):
    url: AnyUrl


@cli.command("play")
def _play(
    path: str, queue: config.Queues.Exchange.Name = typer.Option(None, help="play via queue")
):
    plugin = Plugin(config)
    if queue:
        try:
            path = UrlContainer(url=path).url
        except Exception as e:
            path = pathlib.Path(path)
            if not path.exists():
                typer.echo(f"File {path} not found")
                raise typer.Abort() from e
        if isinstance(path, pathlib.Path):
            with open(path, mode="r+b") as f:
                plugin.publish(f.read(), exchange=queue.value)
        else:
            plugin.publish(path, exchange=queue.value)
        return
    plugin.play(path)


if __name__ == "__main__":
    cli()
