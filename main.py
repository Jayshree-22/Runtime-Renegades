from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create uploads folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve frontend
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

# Upload endpoint
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "message": "Upload successful ✅"
    }