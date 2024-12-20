import random
import string


def get_random_string(string_length):
    alphabet = ''.join([string.ascii_letters, string.digits])
    return ''.join(random.choice(alphabet) for _ in range(string_length))
