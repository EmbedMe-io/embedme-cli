"""Constants used by embedme."""

__version__ = "2024.12.0-dev"

from pathlib import Path

DEFAULT_EMBEDME_PATH = Path.home() / ".embedmeio" / __version__

def get_embedme_package():
    if "dev" in __version__:
        return f"esphome@git+https://github.com/EmbedMe-io/embedme.git@dev"
    return f"esphome@git+https://github.com/EmbedMe-io/embedme.git@{__version__}"
