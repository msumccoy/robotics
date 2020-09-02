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
