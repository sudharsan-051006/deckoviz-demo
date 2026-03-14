from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware

from generator import generate_visual_audiobook

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
JOBS_DIR = "jobs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)


@app.post("/generate")
async def generate(
    pdf: UploadFile = File(...),
    frames: int = Form(...),
    style: str = Form(...)
):

    # unique job id
    job_id = str(uuid.uuid4())

    # save uploaded file
    file_path = f"{UPLOAD_DIR}/{job_id}_{pdf.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)

    # run generation pipeline
    video_path = generate_visual_audiobook(
        file_path,
        frames,
        style,
        job_id
    )

    return {
        "status": "completed",
        "job_id": job_id,
        "video_path": video_path,
        "download_url": f"/download/{job_id}"
    }


@app.get("/download/{job_id}")
def download(job_id: str):

    job_dir = f"{JOBS_DIR}/{job_id}"

    if not os.path.exists(job_dir):
        return {"error": "Job folder not found"}

    zip_path = shutil.make_archive(job_dir, "zip", job_dir)

    return FileResponse(zip_path, filename="visual_audiobook.zip")