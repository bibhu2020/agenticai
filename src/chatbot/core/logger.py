import functools
import datetime

def log_call(func):
    """
    A decorator that logs when a function is called and when it finishes.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        arg_list = ", ".join(
            [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        print(f"[{timestamp}] 🚀 Calling: {func.__name__}({arg_list})")
        try:
            result = func(*args, **kwargs)
            print(f"[{timestamp}] ✅ Finished: {func.__name__}")
            return result
        except Exception as e:
            print(f"[{timestamp}] ❌ Error in {func.__name__}: {e}")
            raise
    return wrapper
