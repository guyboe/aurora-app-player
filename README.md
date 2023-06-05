# Install with dependencies

```bash
pip install --extra-index-url https://test.pypi.org/simple/ -e .
```

# Create config (example)

```yaml
queues:
  url: amqp://guest:guest@localhost
  exchanges:
    play:
      name: aurora.play
      type: fanout
      proxy: proxy/aurora.play
    execute:
      name: aurora.execute
      type: fanout
      proxy: proxy/aurora.execute
  queues:
    - name: aurora.play
      exchange: play
      callback: _play
```

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
