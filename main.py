
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os, shutil, uuid, sqlite3
from PIL import Image
import imagehash

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ IMPORTANT: serve static + uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

DB_PATH = "hashes.db"

# -----------------------
# INIT DB
# -----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            phash TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------
# ROUTES
# -----------------------
@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/about")
def about():
    return FileResponse("static/about.html")

# -----------------------
# UPLOAD
# -----------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        print("UPLOAD HIT ✅")

        # Save file
        filename = f"{uuid.uuid4()}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, filename)

        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Process image
        image = Image.open(path).convert("RGB")
        new_hash = imagehash.phash(image)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT filename, phash FROM images")
        rows = c.fetchall()

        matches = []

        for db_file, db_hash in rows:
            try:
                old_hash = imagehash.hex_to_hash(db_hash)
                diff = new_hash - old_hash
                score = 1 - (diff / 64)

                matches.append({
                    "filename": db_file,
                    "score": float(score)
                })

            except Exception as e:
                print("Skip:", e)

        matches.sort(key=lambda x: x["score"], reverse=True)

        # -----------------------
        # DECIDE RESULT
        # -----------------------
        if len(matches) == 0:
            result = {
                "status": "no_data",
                "message": "Upload another image to compare"
            }
        else:
            top = matches[0]

            if top["score"] > 0.9:
                status = "same"
                message = "🟢 Exact Same Image"
            elif top["score"] > 0.75:
                status = "similar"
                message = "🟡 Similar / Edited Image"
            else:
                status = "different"
                message = "🔴 Completely Different Image"

            result = {
                "status": status,
                "message": message,
                "match": top
            }

        # Save AFTER comparing
        c.execute(
            "INSERT INTO images (filename, phash) VALUES (?, ?)",
            (filename, str(new_hash))
        )
        conn.commit()
        conn.close()

        return JSONResponse(result)

    except Exception as e:
        print("ERROR:", e)
        return JSONResponse({"error": str(e)}, status_code=500)
