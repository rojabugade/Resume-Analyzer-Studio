from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi import UploadFile


class FileTextExtractor:
    """Extract text from supported resume/JD file formats."""

    @staticmethod
    def extract_text_from_bytes(filename: str, data: bytes) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix in {".txt", ".md"}:
            return data.decode("utf-8", errors="ignore")
        if suffix == ".pdf":
            return FileTextExtractor._extract_pdf(data)
        if suffix == ".docx":
            return FileTextExtractor._extract_docx(data)
        raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")

    @staticmethod
    async def extract_text_from_upload(upload: UploadFile) -> str:
        filename = upload.filename or "upload.bin"
        payload = await upload.read()
        await upload.close()
        if not payload:
            raise ValueError(f"Uploaded file is empty: {filename}")
        return FileTextExtractor.extract_text_from_bytes(filename, payload)

    @staticmethod
    def _extract_pdf(data: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pypdf is required for PDF extraction") from exc

        try:
            reader = PdfReader(BytesIO(data))
            chunks = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(chunks).strip()
            if not text:
                raise ValueError("PDF contains no extractable text")
            return text
        except Exception as exc:
            raise ValueError(
                "Unable to parse PDF. File may be encrypted, scanned-only, or invalid."
            ) from exc

    @staticmethod
    def _extract_docx(data: bytes) -> str:
        try:
            from docx import Document
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("python-docx is required for DOCX extraction") from exc

        try:
            document = Document(BytesIO(data))
            lines = [para.text for para in document.paragraphs if para.text]
            text = "\n".join(lines).strip()
            if not text:
                raise ValueError("DOCX contains no extractable text")
            return text
        except Exception as exc:
            raise ValueError("Unable to parse DOCX. File may be invalid or corrupted.") from exc
