import random


def get_random_int():
    return random.randint(0, 1) + 1


def generate_histogram():
    histogram = {1: 0, 2: 0}
    for i in range(100):
        random_int = get_random_int()
        histogram[random_int] += 1
    return histogram


if __name__ == '__main__':
    for i in range(10):
        print(generate_histogram())
