import string
import secrets
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password:str) -> str:
    secret = generate_password_hash(password)
    return secret


def verify_password(guessed:str, hashed:str) -> bool:
    return check_password_hash(hashed, guessed)


def random_key(length:int = 24) -> str:
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
    symbols = list(choices)
    password = ""
    while len(password) < length:
        password += secrets.choice(symbols)

    return password
