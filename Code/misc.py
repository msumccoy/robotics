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
