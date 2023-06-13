# Install with dependencies
```bash
pip install git+https://github.com/guyboe/pydantic-config
pip install git+https://github.com/guyboe/aurora-app-player
```
_You could run `pip install rich` to get a better output_
# Create configs
* Create **config** directory. You can use any name. You can set CONFIG_PATH environment variable with this name if you create directory with different name instead of **config**
* Copy `default.yaml.example` to config directory without **.example** extension

# Validate config

```bash
python -m aurora_app_player config
```

# List all available commands

```bash
python -m aurora_app_player --help
```

# Run consuming queue

```bash
python -m aurora_app_player consume
```

# Play sound from bytes or from url

```bash
python -m aurora_app_player play /path/to/file
python -m aurora_app_player play http://my.host/url/for/file.ext
```
