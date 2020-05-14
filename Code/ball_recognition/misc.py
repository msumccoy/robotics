import time
from functools import wraps


class Wrapper:
    @staticmethod
    def timer(original_func):
        @wraps(original_func)
        def wrapper(*args, **kwargs):
            start = time.time()
            results = original_func(*args, *kwargs)
            print("{} completed in {:.2f} seconds".format(
                original_func.__name__, time.time() - start))
            return results
        return wrapper


class Generic:
    @staticmethod
    def get_int(message):
        not_exit = 1
        while not_exit:
            try:
                input_num = input(message)
                num = int(input_num)
                not_exit = 0
            except TypeError:
                print("{} is not a valid number".format(input_num))
                print("Enter a valid number")
        return num