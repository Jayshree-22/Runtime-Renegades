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

THRESHOLD = 5  # Sensitivity for duplicate detection

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve uploaded images
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

@app.get("/about")
def serve_about():
    return FileResponse("static/about.html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

# Upload endpoint with duplicate detection
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):

    # Generate unique filename
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)

    # Save file temporarily
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Open and process image
    try:
        image = Image.open(file_path)
        image = image.convert("L")          # Convert to grayscale
        image = image.resize((256, 256))   # Normalize size
    except Exception:
        os.remove(file_path)
        return {"error": "Invalid image file"}

    # Generate perceptual hash
    phash = str(imagehash.phash(image))

    # Connect to database
    conn = sqlite3.connect("hashes.db")
    cursor = conn.cursor()

    # Convert new hash
    new_hash = imagehash.hex_to_hash(phash)

    # Fetch all stored hashes
    cursor.execute("SELECT filename, phash FROM images")
    rows = cursor.fetchall()

    # Compare with existing images
    for db_filename, db_phash in rows:
        existing_hash = imagehash.hex_to_hash(db_phash)
        difference = new_hash - existing_hash

        if difference <= THRESHOLD:
            conn.close()

            # ❗ Delete duplicate file
            os.remove(file_path)

            return {
                "message": "Duplicate image detected ⚠️",
                "matched_with": db_filename,
                "difference": difference
            }

    # If no duplicate found → store in DB
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
