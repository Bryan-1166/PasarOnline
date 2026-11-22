
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Mengubah password menjadi hash sebelum disimpan."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Memeriksa password saat pengguna login."""
    return password_hash.verify(password, hashed_password)
