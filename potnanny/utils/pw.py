from passlib.hash import argon2

def hash_password(passwd):
    return argon2.hash(passwd)

def verify_password(guessed, hashed):
    return argon2.verify(guessed, hashed)
