import time


def get_int(prompt="Enter an integer: "):
    while True:
        try:
            num = input(prompt)
            num = int(num)
            return num
        except ValueError:
            print(f"{num} is not a valid integer")


def get_float(prompt="Enter a float: "):
    while True:
        try:
            num = input(prompt)
            num = float(num)
            return num
        except ValueError:
            print(f"{num} is not a valid float")


def get_specific_response(options, prompt=None):
    if prompt is None:
        prompt = "Please enter one of the following:\n"
        if type(options) == dict:
            for key in options:
                prompt += f"    - {key} for {options[key]}\n"
        elif type(options) == list:
            for option in options:
                prompt += f"    - {option}\n"
    if type(options) != dict and type(options) != list:
        raise TypeError(f"options type is not valid: {type(options)}")
    while True:
        response = input(prompt).strip()
        if response in options:
            return response
        else:
            print(f"{response} is not a valid response")


def pretty_time(duration, is_raw=True):
    if is_raw:
        duration = time.time() - duration
    if duration < 1:
        pretty_duration = f"{duration * 1000: .0f}ms"
    elif duration < 60:
        pretty_duration = f"{duration: .0f}s"
    elif duration < 3600:
        duration_ary = [0] * 2
        duration_ary[0] = int(duration / 60)
        duration_ary[1] = int(duration % 60)
        pretty_duration = f"{duration_ary[0]}min {duration_ary[1]}s"
    elif duration < 86400:
        duration_ary = [0] * 3
        duration_ary[0] = int(duration / 3600)
        duration_ary[1] = int((duration % 3600) / 60)
        duration_ary[2] = int((duration % 3600) % 60)
        pretty_duration = (
            f"{duration_ary[0]}h {duration_ary[1]}min {duration_ary[2]}s"
        )
    else:
        duration_ary = [0] * 4
        duration_ary[0] = int(duration / 86400)
        duration_ary[1] = int((duration % 86400) / 3600)
        duration_ary[2] = int(((duration % 86400) % 3600) / 60)
        duration_ary[3] = int(((duration % 86400) % 3600) % 60)
        pretty_duration = (
            f"{duration_ary[0]}day(s) {duration_ary[1]}h "
            f"{duration_ary[2]}min {duration_ary[3]}s"
        )
    return pretty_duration
