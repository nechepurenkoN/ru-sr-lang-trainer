import logging
import sys

global_logger = None


# not thread-safe but who cares
def get_logger() -> logging.Logger:
    global global_logger
    if not global_logger:
        global_logger = create_file_logger("logs")
    return global_logger


def create_file_logger(output_dir) -> logging.Logger:
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f"{output_dir}/log.txt")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    def log_exception(exc_type, exc_value, exc_traceback):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = log_exception

    return logger
