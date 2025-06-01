"""
Celery worker tasks for Blood Test Analysis System (Encrypted + Vector Memory Version)
"""

import time
from celery_app import celery_app
from crewai import Crew, Process
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import help_patients, nutrition_analysis, exercise_planning, verification_task
from util.crypto import decrypt_file
from memory.faiss_memory import add_to_memory
from tools import BloodTestReportTool


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def process_blood_test_analysis(self, encrypted_file_data: str, query: str):
    """
    Celery task to process encrypted blood test PDF and generate analysis.

    Args:
        encrypted_file_data (str): Encrypted file content (base64-encoded).
        query (str): The user's question or prompt.

    Returns:
        dict: Structured output from CrewAI agents.
    """
    try:
        print(f"[TASK] Starting blood test analysis for query: {query}")
        start = time.time()

        # Decrypt PDF bytes
        pdf_bytes = decrypt_file(encrypted_file_data)

        # Parse PDF using our custom tool (uses pdfplumber internally)
        tool = BloodTestReportTool()
        blood_text = tool.read_pdf_bytes(pdf_bytes)

        # Store parsed report in vector memory
        add_to_memory(blood_text, metadata={"source": "blood_report", "query": query})
        print("[MEMORY] Blood test report added to FAISS vector store")

        # Setup CrewAI
        crew = Crew(
            agents=[verifier, doctor, nutritionist, exercise_specialist],
            tasks=[verification_task, help_patients, nutrition_analysis, exercise_planning],
            process=Process.sequential,
            verbose=True,
            max_rpm=25,
        )

        # Run CrewAI with inputs
        results = crew.kickoff(inputs={"query": query, "blood_text": blood_text})
        duration = time.time() - start

        print(f"[SUCCESS] Analysis completed in {duration:.2f}s")

        return {
            "verification_result": str(crew.tasks[0].output),
            "doctor_analysis": str(crew.tasks[1].output),
            "nutrition_advice": str(crew.tasks[2].output),
            "exercise_plan": str(crew.tasks[3].output),
            "processing_time": f"{duration:.2f} seconds"
        }

    except Exception as e:
        print(f"[ERROR] Task failed: {e}")
        raise self.retry(exc=e)
