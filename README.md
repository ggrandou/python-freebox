# python-freebox

Python client library for the Freebox API (v16).

## Installation

```bash
source setup_env.sh
```

## Usage

```python
from freebox import Freebox
from pathlib import Path

fb = Freebox(
    app_id="com.example.myapp",
    app_name="My App",
    app_version="1.0",
    device_name="my-pc",
    token_file=Path("~/.freebox_token"),
)
fb.open()
status = fb.get("connection/status/")
fb.close()
```
