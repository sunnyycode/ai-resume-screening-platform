import os
import re
from pypdf import PdfReader
from docx import Document

class ResumeParserError(Exception):
    """Custom exception for resume parsing errors."""
    pass

class ResumeParser:
    """Service to parse and extract structured info from PDF, DOCX, and TXT resumes."""

    EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    PHONE_REGEX = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"

    @classmethod
    def extract_text_from_file(cls, file_path: str) -> str:
        """Extract plain text from PDF, DOCX, or TXT file with comprehensive error handling."""
        if not os.path.exists(file_path):
            raise ResumeParserError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ResumeParserError("The uploaded file is empty (0 bytes).")

        _, ext = os.path.splitext(file_path)
        ext = ext.lower().replace(".", "")

        try:
            if ext == "pdf":
                return cls._extract_from_pdf(file_path)
            elif ext == "docx":
                return cls._extract_from_docx(file_path)
            elif ext == "txt":
                return cls._extract_from_txt(file_path)
            else:
                raise ResumeParserError(f"Unsupported file format: .{ext}. Allowed formats: .pdf, .docx, .txt")
        except ResumeParserError:
            raise
        except Exception as e:
            raise ResumeParserError(f"Failed to read {ext.upper()} file: {str(e)}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF pages using pypdf."""
        try:
            reader = PdfReader(file_path)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    raise ResumeParserError("PDF is password protected and cannot be read.")

            extracted_pages = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(page_text)

            full_text = "\n".join(extracted_pages).strip()
            if not full_text:
                raise ResumeParserError("No readable text found in PDF. It might be scanned or image-based.")
            return full_text
        except Exception as e:
            if "ResumeParserError" in type(e).__name__:
                raise
            raise ResumeParserError(f"Corrupted or invalid PDF file: {str(e)}")

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX paragraphs and tables using python-docx."""
        try:
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

            # Also extract from tables
            table_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_data:
                        table_text.append(" | ".join(row_data))

            combined = "\n".join(paragraphs + table_text).strip()
            if not combined:
                raise ResumeParserError("No readable text found in DOCX file.")
            return combined
        except Exception as e:
            if "ResumeParserError" in type(e).__name__:
                raise
            raise ResumeParserError(f"Corrupted or invalid DOCX document: {str(e)}")

    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from TXT with multiple encoding fallbacks."""
        encodings = ["utf-8", "latin-1", "cp1252", "ascii"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read().strip()
                if content:
                    return content
            except (UnicodeDecodeError, Exception):
                continue
        raise ResumeParserError("Unable to decode text file. Ensure it is encoded in UTF-8 or standard ASCII.")

    @classmethod
    def extract_candidate_metadata(cls, text: str, fallback_filename: str = "") -> dict:
        """
        Extract candidate contact details:
        - Candidate Name (first prominent non-empty line or inferred from filename)
        - Email
        - Phone
        """
        email_match = re.search(cls.EMAIL_REGEX, text)
        email = email_match.group(0) if email_match else None

        phone_match = re.search(cls.PHONE_REGEX, text)
        phone = phone_match.group(0).strip() if phone_match else None

        # Extract name heuristic
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        candidate_name = None

        # Check for explicit "Name: John Doe"
        for line in lines[:10]:
            name_match = re.match(r"^(?:name|candidate name|full name)\s*[:\-]\s*(.+)$", line, re.IGNORECASE)
            if name_match:
                candidate_name = name_match.group(1).strip()
                break

        # If not explicit, take the first line if it looks like a person's name (2-4 words, no email/phone)
        if not candidate_name and lines:
            first_line = lines[0]
            words = first_line.split()
            if 2 <= len(words) <= 4 and not re.search(r"[@#/\\0-9]|(?:resume|curriculum|cv)", first_line, re.IGNORECASE):
                candidate_name = first_line

        # Fallback to filename if heuristics yield nothing
        if not candidate_name and fallback_filename:
            base_name, _ = os.path.splitext(os.path.basename(fallback_filename))
            cleaned_base = re.sub(r"[-_]", " ", base_name)
            cleaned_base = re.sub(r"(?i)resume|cv|application", "", cleaned_base).strip()
            if cleaned_base:
                candidate_name = cleaned_base.title()

        if not candidate_name:
            candidate_name = "Candidate"

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone
        }
