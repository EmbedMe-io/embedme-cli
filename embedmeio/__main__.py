import importlib
import logging
import os
import re
import subprocess
import sys
import venv
from .const import DEFAULT_EMBEDME_PATH, get_embedme_package

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger("embedmeio")


def check_venv():
    # First check for the presence of embedmeio
    if importlib.util.find_spec("esphome") and importlib.util.find_spec("esphome.embedmeio"):
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
    return False


def ask(prompt):
    prompt = re.sub(r"\n +", "\n", prompt)
    response = input(prompt + " (y/n)? ").strip().lower()
    if response != "y" and response != "yes":
        return False
    return True




def activate_venv():
    import os

    if not DEFAULT_EMBEDME_PATH.exists() or not DEFAULT_EMBEDME_PATH.is_dir():
        return False
    py_executable = DEFAULT_EMBEDME_PATH / "bin" / "python"
    if not py_executable.exists() or not os.access(py_executable, os.X_OK):
        return False
    embedme_main = DEFAULT_EMBEDME_PATH / "bin" / "embedmeio"
    if not embedme_main.exists():
        return False

    _LOGGER.info("Activating EmbedMe venv in %s", DEFAULT_EMBEDME_PATH)
    os.execv(py_executable, ["embedmeio", "-m", "embedmeio", *sys.argv[1:]])


def create_venv():
    if not ask(f"""
            EmbedMe requires a venv to run; a custom venv can be created in this folder:

            {DEFAULT_EMBEDME_PATH}.

            Do you want to create a venv in that location for future use"""):
        return False

    if DEFAULT_EMBEDME_PATH.exists():
        if not ask(
                f"""
            Folder {DEFAULT_EMBEDME_PATH} already exists, do you want to overwrite it"""
        ):
            return False
    builder = venv.EnvBuilder(
        with_pip=True,
        clear=True,
        symlinks=True,
    )
    builder.create(DEFAULT_EMBEDME_PATH)  # type: ignore
    _LOGGER.info("EmbedMe venv created in %s", DEFAULT_EMBEDME_PATH)
    _LOGGER.info("Installing EmbedMe in %s", DEFAULT_EMBEDME_PATH)
    os.environ["PATH"] = f"{DEFAULT_EMBEDME_PATH}/bin:{os.environ['PATH']}"
    os.environ["VIRTUAL_ENV"] = str(DEFAULT_EMBEDME_PATH)
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
    if check_venv():
        return run_embedme()
    activate_venv()
    # if activate_venv returns, it was not activated
    if not create_venv():
        return 1
    activate_venv()
    return run_embedme()


if __name__ == "__main__":
    sys.exit(main())
