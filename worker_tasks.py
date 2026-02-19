"""
Celery worker tasks for Blood Test Analysis System (Encrypted + Vector Memory Version)
"""

import time
import json
from celery_app import celery_app
from crewai import Crew, Process
from agents import doctor, verifier, nutritionist, exercise_specialist, summary_agent
from task import help_patients, nutrition_analysis, exercise_planning, verification_task, specific_query_answer
from util.crypto import decrypt_file
from memory.faiss_memory import add_to_memory
from tools import BloodTestReportTool
from database import update_analysis


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def process_blood_test_analysis(self, blood_text: str, query: str):
    """
    Celery task to generate analysis from blood test text.

    Args:
        blood_text (str): Extracted text from the blood test PDF.
        query (str): The user's question or prompt.

    Returns:
        dict: Structured output from CrewAI agents.
    """
    try:
        print(f"[TASK] Starting blood test analysis for query: {query}")
        update_analysis(self.request.id, "processing")
        start = time.time()

        # Store parsed report in vector memory
        add_to_memory(blood_text, metadata={"source": "blood_report", "query": query})
        print("[MEMORY] Blood test report added to FAISS vector store")

        # Setup CrewAI
        crew = Crew(
            agents=[verifier, doctor, nutritionist, exercise_specialist, summary_agent],
            tasks=[verification_task, help_patients, nutrition_analysis, exercise_planning, specific_query_answer],
            process=Process.sequential,
            verbose=True,
            max_rpm=25,
        )

        # Run CrewAI with inputs
        results = crew.kickoff(inputs={"query": query, "blood_text": blood_text})
        duration = time.time() - start

        print(f"[SUCCESS] Analysis completed in {duration:.2f}s")

        result_data = {
            "verification_result": str(crew.tasks[0].output),
            "doctor_analysis": str(crew.tasks[1].output),
            "nutrition_advice": str(crew.tasks[2].output),
            "exercise_plan": str(crew.tasks[3].output),
            "direct_answer": str(crew.tasks[4].output),
            "processing_time": f"{duration:.2f} seconds"
        }
        
        update_analysis(self.request.id, "completed", result_json=json.dumps(result_data))
        
        return result_data

    except Exception as e:
        print(f"[ERROR] Task failed: {e}")
        update_analysis(self.request.id, "failed")
        raise self.retry(exc=e)
