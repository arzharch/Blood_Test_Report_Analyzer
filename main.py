from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import traceback
import json
from celery.result import AsyncResult

from celery_app import celery_app
from worker_tasks import process_blood_test_analysis
from util.crypto import encrypt_file, decrypt_file
from database import get_analysis_by_id
from tools import BloodTestReportTool

app = FastAPI(title="Blood Test Report Analyser")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.environ["OTEL_SDK_DISABLED"] = "true"
from database import create_tables

@app.on_event("startup")
def init():
    create_tables()


@app.get("/")
async def root():
    return {"message": "Blood Test Report Analyser API is running"}


@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarize my blood test report")
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        file_id = str(uuid.uuid4())
        encrypted_path = os.path.join(UPLOAD_DIR, f"{file_id}.enc")

        content = await file.read()

        # ✅ Use BloodTestReportTool to read content from PDF bytes
        reader = BloodTestReportTool()
        blood_text = reader.read_pdf_bytes(file_bytes=content)


        if not blood_text.strip():
            raise HTTPException(status_code=400, detail="Uploaded PDF has no readable text.")

        # ✅ Encrypt the raw bytes of the original PDF
        encrypted_string = encrypt_file(content)
        print(f"[INFO] PDF encrypted successfully")

        # ✅ Queue Celery task
        task = process_blood_test_analysis.delay(encrypted_string, query.strip())


        return {
            "status": "queued",
            "task_id": task.id,
            "analysis_id": file_id,
            "file_processed": file.filename,
            "query": query
        }

    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue analysis task: {str(e)}\n{error_details}"
        )


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        status = task_result.status

        response = {
            "task_id": task_id,
            "status": status,
        }

        if status == "SUCCESS":
            response["result"] = task_result.result
        elif status == "FAILURE":
            response["error"] = str(task_result.result)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


