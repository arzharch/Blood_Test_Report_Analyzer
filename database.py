import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from util.crypto import encrypt_file, decrypt_file

# DB setup
DATABASE_URL = "sqlite:///blood_analysis.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True)
    task_id = Column(String, index=True)
    filename = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    result_json = Column(Text)
    encrypted_file = Column(LargeBinary)  # PDF file encrypted
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)


def create_analysis_record(id, filename, query, task_id, encrypted_file_bytes):
    """Create a new analysis record in the database."""
    session = SessionLocal()
    result = AnalysisResult(
        id=id,
        task_id=task_id,
        filename=filename,
        query=query,
        encrypted_file=encrypted_file_bytes,
        status="queued"
    )
    session.add(result)
    session.commit()
    session.close()


def update_analysis(task_id, status, result_json=None):
    """Update analysis status and result."""
    session = SessionLocal()
    result = session.query(AnalysisResult).filter_by(task_id=task_id).first()
    if result:
        result.status = status
        if result_json:
            result.result_json = result_json
        session.commit()
    session.close()


def save_analysis(id, filename, query, result_json, file_path, status="completed"):
    """Encrypt and store analysis result and file."""
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    encrypted_string = encrypt_file(file_bytes)

    session = SessionLocal()
    result = AnalysisResult(
        id=id,
        filename=filename,
        query=query,
        result_json=result_json,
        encrypted_file=encrypted_string.encode("utf-8"),
        status=status
    )
    session.add(result)
    session.commit()
    session.close()


def get_all_analyses():
    """Retrieve all analysis records from the database."""
    session = SessionLocal()
    results = session.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()
    session.close()
    return results
def retrieve_encrypted_file(analysis_id: str):
    """Decrypt and return the original file contents."""
    session = SessionLocal()
    result = session.query(AnalysisResult).filter_by(id=analysis_id).first()
    session.close()

    if result and result.encrypted_file:
        try:
            # result.encrypted_file is stored as bytes(base64_encoded_string)
            encrypted_data_str = result.encrypted_file.decode("utf-8")
            decrypted_data = decrypt_file(encrypted_data_str)
            return decrypted_data, result.filename
        except Exception as e:
            raise ValueError("Decryption failed") from e
    else:
        raise FileNotFoundError("Analysis ID not found or file missing")
    
def get_analysis_by_id(analysis_id: str):
    """Retrieve analysis record from the database by ID"""
    session = SessionLocal()
    result = session.query(AnalysisResult).filter_by(id=analysis_id).first()
    session.close()
    return result

