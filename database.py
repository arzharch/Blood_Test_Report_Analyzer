import os
import base64
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

# Load or create encryption key
ENCRYPTION_KEY_PATH = "secret.key"
if os.path.exists(ENCRYPTION_KEY_PATH):
    with open(ENCRYPTION_KEY_PATH, "rb") as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(ENCRYPTION_KEY_PATH, "wb") as f:
        f.write(key)

fernet = Fernet(key)

# DB setup
DATABASE_URL = "sqlite:///blood_analysis.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    result_json = Column(Text)
    encrypted_file = Column(LargeBinary)  # PDF file encrypted
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)


def save_analysis(id, filename, query, result_json, file_path, status="completed"):
    """Encrypt and store analysis result and file."""
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    encrypted_data = fernet.encrypt(file_bytes)

    session = SessionLocal()
    result = AnalysisResult(
        id=id,
        filename=filename,
        query=query,
        result_json=result_json,
        encrypted_file=encrypted_data,
        status=status
    )
    session.add(result)
    session.commit()
    session.close()
def retrieve_encrypted_file(analysis_id: str):
    """Decrypt and return the original file contents."""
    session = SessionLocal()
    result = session.query(AnalysisResult).filter_by(id=analysis_id).first()
    session.close()

    if result and result.encrypted_file:
        try:
            decrypted_data = fernet.decrypt(result.encrypted_file)
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

