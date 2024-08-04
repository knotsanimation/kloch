import logging
import logging.handlers
import sys
from typing import List
from typing import Optional

import kloch

LOGGER = logging.getLogger(__name__)


def main(argv: Optional[List[str]] = None):
    """
    Args:
        argv: command line arguments. from sys.argv if not provided
    """
    config = kloch.get_config()
    cli = kloch.get_cli(argv, config=config)
    log_level = logging.DEBUG if cli.debug else config.cli_logging_default_level

    formatter = logging.Formatter(config.cli_logging_format, style="{")

    logging.root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)

    for log_path in config.cli_logging_paths:
        log_path.parent.mkdir(exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            log_path,
            # keep in sync with config option
            maxBytes=262144,
            backupCount=1,
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

    LOGGER.debug(f"starting {kloch.__name__} v{kloch.__version__}")
    LOGGER.debug(f"retrieved cli with args={cli._args}")

    sys.exit(cli.execute())


if __name__ == "__main__":
    main()  # pragma: no cover
