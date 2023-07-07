import os
import scrypt
import hashlib
from potnanny.utils.serial import SERIAL_NUMBER

MYSALT = os.getenv('POTNANNY_SECRET', SERIAL_NUMBER)

def hash_password(password):
    secret = scrypt.hash(password, MYSALT)
    return hashlib.sha256(secret).hexdigest()

def verify_password(guessed, hashed):
    secret = hash_password(guessed)
    return secret == hashed
