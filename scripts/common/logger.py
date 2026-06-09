import logging


def get_logger(name: str = "aws-retail-data-platform") -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

    return logger