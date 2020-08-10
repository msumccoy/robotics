def get_int(prompt="Enter motion num: "):
    while True:
        try:
            num = input(prompt)
            num = int(num)
            return num
        except ValueError:
            print(f"{num} is not a valid integer")
