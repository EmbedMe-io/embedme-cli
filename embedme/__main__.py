import importlib
import logging
import os
import subprocess
import sys
import venv
from const import DEFAULT_EMBEDME_PATH, __version__
from embedme.const import get_embedme_package

_LOGGER = logging.getLogger(__name__)


def check_venv():
    # First check for the presence of embedme
    if importlib.util.find_spec("esphome") and importlib.util.find_spec("esphome.embedme"):
        return True

    # Are we running in a venv?
    if sys.prefix != sys.base_prefix:
        # if esphome is installed, it's not the right one
        if importlib.util.find_spec("esphome"):
            _LOGGER.error(
                """EmbedMe should be run in a venv with the EmbedMe version of esphome installed.
                This venv (%s)has a different version of esphome installed", sys.prefix
                """
            )
            return False

        return True
    # TODO create and populate a venv
    _LOGGER.error("EmbedMe should be run in a venv (virtual environment)")
    return False


def activate_venv():
    import os

    if not DEFAULT_EMBEDME_PATH.exists(follow_symlinks=True) or not DEFAULT_EMBEDME_PATH.is_dir():
        return False
    py_executable = DEFAULT_EMBEDME_PATH / "bin" / "python"
    if not py_executable.exists(follow_symlinks=True) or not os.access(py_executable, os.X_OK):
        return False
    _LOGGER.info("Activating EmbedMe venv in %s", DEFAULT_EMBEDME_PATH)
    os.execv(py_executable, [py_executable, "-m", "embedme", *sys.argv[1:]])

def create_venv():
    _LOGGER.info("EmbedMe requires a venv to run, a custom venv can be created in %s", DEFAULT_EMBEDME_PATH)
    response = input("Do you want to create a venv(y/n)?")
    if response.lower() != "y" or response.lower() != "yes":
        return False
    builder = venv.EnvBuilder(
        with_pip=True,
        clear=False,
        symlinks=True,
    )
    builder.create(DEFAULT_EMBEDME_PATH)  # type: ignore
    _LOGGER.info(
        "EmbedMe venv created in %s, now installing the EmbedMe version of esphome", DEFAULT_EMBEDME_PATH
    )
    os.environ["VIRTUAL_ENV"] = str(DEFAULT_EMBEDME_PATH)
    os.environ["PATH"] = str(DEFAULT_EMBEDME_PATH / "bin") + os.pathsep + os.environ["PATH"]

    subprocess.run(["python", "-m", "pip", "install", get_embedme_package()])
    return True


def run_embedme():
    from esphome.__main__ import run_esphome
    from esphome.core import EsphomeError

    try:
        return run_esphome(sys.argv)
    except EsphomeError as e:
        _LOGGER.error(e)
        return 1
    except KeyboardInterrupt:
        return 1


def main():
    if not check_venv() and not activate_venv():
        return 1
    if not create_venv() or not activate_venv():
        return 1
    return run_embedme()


if __name__ == "__main__":
    sys.exit(main())
