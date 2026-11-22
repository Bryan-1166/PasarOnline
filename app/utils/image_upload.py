
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException

# Lokasi folder utama proyek
BASE_DIR = Path(__file__).resolve().parents[2]

# Folder penyimpanan foto produk
UPLOAD_DIR = BASE_DIR / "public" / "images" / "products"

# Format foto yang diperbolehkan
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png"
}

# Batas ukuran foto: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


async def save_product_image(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Format foto harus JPG, JPEG, atau PNG"
        )

    # Baca maksimal 5 MB + 1 byte untuk mendeteksi file terlalu besar
    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="File foto tidak boleh kosong"
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Ukuran foto maksimal 5 MB"
        )

    # Buat nama file unik
    extension = ALLOWED_TYPES[file.content_type]
    filename = f"{uuid4().hex}{extension}"

    # Pastikan folder tersedia
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Simpan foto
    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(content)

    # Kembalikan alamat foto
    return f"/public/images/products/{filename}"
