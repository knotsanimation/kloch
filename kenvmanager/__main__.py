import logging
import sys

import kenvmanager

LOGGER = logging.getLogger(__name__)


def main():
    cli = kenvmanager.get_cli()
    log_level = logging.DEBUG if cli.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    LOGGER.debug(f"starting {kenvmanager.__name__} v{kenvmanager.__version__}")
    LOGGER.debug(f"retrieved cli with args={cli._args}")

    if cli.profile_paths:
        LOGGER.debug(f"adding {len(cli.profile_paths)} profile locations")
        [kenvmanager.add_profile_location(path) for path in cli.profile_paths]

    sys.exit(cli.execute())


if __name__ == "__main__":
    main()
