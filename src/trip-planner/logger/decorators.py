import functools
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_entry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_list = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        logger.info(f"➡️ Entering: {func.__name__}({', '.join(arg_list)})")
        return func(*args, **kwargs)
    return wrapper
