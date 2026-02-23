from cryptography.fernet import Fernet
from schemas import settings
key = settings.encryption_key.encode("utf-8")

cipher = Fernet(key)

def encrypt_token(token: str) -> str:
    """
    Encrypts a token and returns it as a string.
    """
    token_bytes = token.encode('utf-8')
    encrypted_bytes = cipher.encrypt(token_bytes)
    return encrypted_bytes.decode('utf-8')

def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypts a previously encrypted token.
    """
    encrypted_bytes = encrypted_token.encode('utf-8')
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return decrypted_bytes.decode('utf-8')

