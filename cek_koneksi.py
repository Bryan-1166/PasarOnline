
from sqlalchemy import text
from app.database import engine

try:
    with engine.connect() as connection:
        hasil = connection.execute(
            text("SELECT current_database()")
        )

        print("Koneksi database berhasil!")
        print("Database:", hasil.scalar())

except Exception as e:
    print("Koneksi database gagal!")
    print("Error:", e)
