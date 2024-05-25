import logging
import sys

import kloch

LOGGER = logging.getLogger(__name__)


def main():
    config = kloch.get_config()
    cli = kloch.get_cli()
    log_level = logging.DEBUG if cli.debug else config.cli_logging_default_level
    logging.basicConfig(
        level=log_level,
        format=config.cli_logging_format,
        style="{",
        stream=sys.stdout,
    )
    LOGGER.debug(f"starting {kloch.__name__} v{kloch.__version__}")
    LOGGER.debug(f"retrieved cli with args={cli._args}")

    if cli.profile_paths:
        LOGGER.debug(f"adding {len(cli.profile_paths)} profile locations")
        [kloch.add_profile_location(path) for path in cli.profile_paths]

    sys.exit(cli.execute())


if __name__ == "__main__":
    main()
