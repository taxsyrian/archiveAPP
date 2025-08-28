# archive_server.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
from cryptography.fernet import Fernet

app = FastAPI()
UPLOAD_DIR = "archives"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SECRET_KEY = b'your-32-byte-base64-key-here'
fernet = Fernet(SECRET_KEY)

@app.post("/upload")
async def upload_archive(file: UploadFile = File(...)):
    filename = file.filename
    if not filename.endswith(".zip"):
        return JSONResponse(status_code=400, content={"error": "الملف يجب أن يكون مضغوطًا بصيغة ZIP"})

    encrypted_data = await file.read()
    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception:
        return JSONResponse(status_code=400, content={"error": "فشل فك التشفير"})

    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        f.write(decrypted_data)

    return {"message": "تم استلام الملف بنجاح", "filename": filename}
