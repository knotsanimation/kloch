import logging
import sys

import kenvmanager

LOGGER = logging.getLogger(__name__)


def main():
    cli = kenvmanager.getCli()
    log_level = logging.DEBUG if cli.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    LOGGER.info(f"Starting {kenvmanager.__name__} v{kenvmanager.__version__}")
    LOGGER.debug(f"retrieved cli with args={cli._args}")
    sys.exit(cli.execute())


if __name__ == "__main__":
    main()
