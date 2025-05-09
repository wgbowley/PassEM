import hashlib
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt(account: str, master_pass: str) -> dict:
    """
    Encrypts an account using AES-GCM.
    """
    salt = get_random_bytes(AES.block_size)
    private_key = hashlib.scrypt(
        master_pass.encode(),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )
    cipher = AES.new(private_key, AES.MODE_GCM)
    encrypted_text, tag = cipher.encrypt_and_digest(account.encode('utf-8'))

    return {
        'account': b64encode(encrypted_text).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8'),
        'nonce': b64encode(cipher.nonce).decode('utf-8'),
        'tag': b64encode(tag).decode('utf-8')
    }

def decrypt(encrypted_account: dict, password: str) -> dict:
    """
    Decrypts an account using AES-GCM.
    """
    encrypted_text = b64decode(encrypted_account['account'])
    salt = b64decode(encrypted_account['salt'])
    nonce = b64decode(encrypted_account['nonce'])
    tag = b64decode(encrypted_account['tag'])

    private_key = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )
    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)
    decrypted_text = cipher.decrypt_and_verify(encrypted_text, tag)

    return json.loads(decrypted_text.decode('utf-8'))
