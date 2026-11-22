
from app.utils.security import hash_password, verify_password

# Password contoh untuk pengujian
password = "PasswordContoh123!"

# Mengubah password menjadi hash
hashed = hash_password(password)

print("Password asli:", password)
print("Password hash:", hashed)

# Menguji password yang benar
print("Password benar:", verify_password(password, hashed))

# Menguji password yang salah
print("Password salah:", verify_password("PasswordSalah", hashed))
