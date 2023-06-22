import os
import scrypt
import hashlib

MYSALT = os.getenv('POTNANNY_SECRET', os.urandom(24))

def hash_password(password):
    secret = scrypt.hash(password, MYSALT)
    return hashlib.sha256(secret).hexdigest()

def verify_password(guessed, hashed):
    secret = hash_password(guessed)
    return secret == hashed
