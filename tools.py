import io
from PyPDF2 import PdfReader


class BloodTestReportTool:
    def read_pdf_bytes(self, file_bytes: bytes) -> str:
        """
        Reads and extracts text from PDF bytes using PyPDF2.
        Returns a cleaned text string.
        """
        try:
            pdf_stream = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_stream)

            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text.replace("\n\n", "\n") + "\n"

            return full_text.strip()

        except Exception as e:
            raise ValueError(f"Failed to parse PDF using PyPDF2: {e}")
