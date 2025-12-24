import random
import string


ASCII_CHARS = string.ascii_letters
DIGITS_CHARS = string.digits
# TOKEN_CHARS = ASCII_CHARS + '-' + DIGITS_CHARS
TOKEN_CHARS = ASCII_CHARS + DIGITS_CHARS


def get_a_token(length=20, charset=None):
    CHARS = {
        'ascii': ASCII_CHARS,
        'digits': DIGITS_CHARS,
    }.get(charset, TOKEN_CHARS)
    return ''.join([random.choice(CHARS) for x in range(length)])
