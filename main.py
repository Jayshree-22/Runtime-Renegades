from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from PIL import Image
import imagehash
import sqlite3

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve uploaded images (optional but useful)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Create uploads folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect("hashes.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        phash TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# Serve frontend
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

# Upload endpoint with hashing
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):

    # Generate unique filename
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Open image
    try:
        image = Image.open(file_path)
    except Exception:
        return {"error": "Invalid image file"}

    # Generate perceptual hash (pHash)
    phash = str(imagehash.phash(image))

    # Store in database
    conn = sqlite3.connect("hashes.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO images (filename, phash) VALUES (?, ?)",
        (unique_name, phash)
    )

    conn.commit()
    conn.close()

    return {
        "filename": unique_name,
        "phash": phash,
        "message": "Upload + hash stored ✅"
    }
