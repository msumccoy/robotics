import time
from datetime import datetime
from functools import wraps

from config import LogConf
from log_master import LogMaster


def timer(orig_func):
    # Simple wrapper to time function execution time.
    @wraps(orig_func)
    def wrapper(*args, output_name=None, **kwargs):
        start = time.time()
        return_value = orig_func(*args, **kwargs)
        time_elapsed = time.time() - start
        time_elapsed = "{:.2f}".format(time_elapsed)
        if output_name is None:
            name = orig_func.__name__
        else:
            name = output_name
            if "thread" in output_name:
                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger = LogMaster.get_inst()
                message = LogConf.T_THREAD_COMPLETE.substitute(
                    date_t=date_time, thread=output_name, dur=time_elapsed
                )
                logger.log(message)
        print("{} ran in {} seconds".format(
            name, time_elapsed)
        )
        return return_value
    return wrapper
