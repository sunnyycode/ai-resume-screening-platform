import os
import pytest
from backend.services.resume_parser import ResumeParser, ResumeParserError

SAMPLE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "sample_resumes")

def test_extract_text_from_txt():
    txt_path = os.path.join(SAMPLE_DIR, "alice_backend_developer.txt")
    assert os.path.exists(txt_path)
    text = ResumeParser.extract_text_from_file(txt_path)
    assert len(text) > 100
    assert "Python" in text
    assert "Flask" in text

def test_extract_text_from_docx():
    docx_path = os.path.join(SAMPLE_DIR, "carol_ml_engineer.docx")
    assert os.path.exists(docx_path)
    text = ResumeParser.extract_text_from_file(docx_path)
    assert len(text) > 100
    assert "Carol Danvers" in text
    assert "Machine Learning" in text

def test_extract_text_from_pdf():
    pdf_path = os.path.join(SAMPLE_DIR, "david_fullstack_developer.pdf")
    assert os.path.exists(pdf_path)
    text = ResumeParser.extract_text_from_file(pdf_path)
    assert len(text) > 50
    assert "David" in text or "Full Stack" in text

def test_missing_file_raises_error():
    with pytest.raises(ResumeParserError) as exc:
        ResumeParser.extract_text_from_file("non_existent_file.pdf")
    assert "File not found" in str(exc.value)

def test_empty_file_raises_error(tmp_path):
    empty_file = tmp_path / "empty_resume.txt"
    empty_file.write_text("")
    with pytest.raises(ResumeParserError) as exc:
        ResumeParser.extract_text_from_file(str(empty_file))
    assert "empty" in str(exc.value).lower()

def test_unsupported_format_raises_error(tmp_path):
    unsupported_file = tmp_path / "resume.xyz"
    unsupported_file.write_text("Some random content")
    with pytest.raises(ResumeParserError) as exc:
        ResumeParser.extract_text_from_file(str(unsupported_file))
    assert "Unsupported file format" in str(exc.value)

def test_extract_candidate_metadata():
    raw_text = """John Doe
Email: john.doe@example.com
Phone: +1-555-234-5678
Experienced Software Developer with Python and Flask.
"""
    metadata = ResumeParser.extract_candidate_metadata(raw_text)
    assert metadata["name"] == "John Doe"
    assert metadata["email"] == "john.doe@example.com"
    assert "555" in metadata["phone"]
