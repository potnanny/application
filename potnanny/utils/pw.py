import os
import scrypt
import hashlib
import string
import secrets
from potnanny.utils.serial import SERIAL_NUMBER

MYSALT = os.getenv('POTNANNY_SECRET', SERIAL_NUMBER)

def hash_password(password):
    secret = scrypt.hash(password, MYSALT)
    return hashlib.sha256(secret).hexdigest()


def verify_password(guessed, hashed):
    secret = hash_password(guessed)
    return secret == hashed


def random_key(length=24):
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
    symbols = list(choices)
    password = ""
    while len(password) < length:
        password += secrets.choice(symbols)

    return password
