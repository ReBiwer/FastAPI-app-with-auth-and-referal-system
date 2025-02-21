import string
import random


def get_ref_code(len_code: int = 6):
    characters = string.digits + string.ascii_uppercase
    random_string = ''.join(random.choice(characters) for _ in range(len_code))
    return random_string
