import io
from PyPDF2 import PdfReader


class BloodTestReportTool:
    """
    A tool for processing blood test reports in PDF format.
    This class encapsulates the functionality to read and extract text from PDF files,
    making it easier to handle blood test report data.
    """

    def read_pdf_bytes(self, file_bytes: bytes) -> str:
        """
        Reads and extracts text from PDF bytes using PyPDF2.

        This method takes the byte content of a PDF file, processes it,
        and extracts the text from each page. It then cleans up the
        extracted text by removing excessive newlines, making it
        more suitable for further analysis.

        Args:
            file_bytes: The byte content of the PDF file.

        Returns:
            A cleaned text string containing the content of the PDF.

        Raises:
            ValueError: If the PDF parsing fails.
        """
        try:
            # Create a byte stream from the input bytes
            pdf_stream = io.BytesIO(file_bytes)
            # Initialize the PDF reader
            reader = PdfReader(pdf_stream)

            full_text = ""
            # Iterate through each page of the PDF
            for page in reader.pages:
                # Extract text from the page
                text = page.extract_text()
                if text:
                    # Clean up and append the text
                    full_text += text.replace("\n\n", "\n") + "\n"

            # Return the full text with leading/trailing whitespace removed
            return full_text.strip()

        except Exception as e:
            # Raise an exception if PDF parsing fails
            raise ValueError(f"Failed to parse PDF using PyPDF2: {e}")
