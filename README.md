# Install with dependencies

```bash
pip install -e .
pip install --extra-index-url https://test.pypi.org/simple/ pydantic-another-config
```

# Copy `default.yaml.example` to config directory

# Validate config

```bash
python -m commands aurora_app_player config
```

# List all available commands

```bash
python -m commands aurora_app_player --help
```

# Run consuming queue

```bash
python -m commands aurora_app_player consume
```
