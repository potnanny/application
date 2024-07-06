import os
import base64
from cryptography.fernet import Fernet


def get_fernet_key() -> bytes:
    required_size = 32

    k = os.getenv('POTNANNY_SECRET')
    if k is None:
        raise ValueError('POTNANNY_SECRET key not found')

    if len(k) > required_size:
        k = k[:required_size]
    elif len(k) < 32:
        k = k.zfill(required_size)

    return base64.urlsafe_b64encode(k.encode())


def encrypt_str(data:str) -> str:
    key = get_fernet_key()
    f = Fernet(key)

    if isinstance(data, str):
        data = data.encode()

    return f.encrypt(data).decode()


def decrypt_str(data:str) -> str:
    key = get_fernet_key()
    f = Fernet(key)

    if isinstance(data, str):
        data = data.encode()

    return f.decrypt(data).decode()
