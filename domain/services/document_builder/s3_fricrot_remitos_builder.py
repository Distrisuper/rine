import base64
import json
import os
from pathlib import Path
from typing import Any

import httpx
from sqlmodel import Session

from domain.services.document_builder.document_builder_interface import DocumentBuilder


class S3FricRotRemitosBuilder(DocumentBuilder):
    """Retrieves pre-generated PDF from S3 (Fricrot remitos)."""

    def build(self, job: Any, session: Session) -> bytes:
        data = json.loads(job.payload)

        extra = self._get_extra_data(data)

        if pdf_base64 := data.get("pdf_base64") or extra.get("pdf_base64"):
            return base64.b64decode(pdf_base64)

        if pdf_url := data.get("pdf_url") or extra.get("pdf_url"):
            return self._download_pdf(pdf_url)

        if ftp_filename := data.get("ftp_filename") or extra.get("ftp_filename"):
            return self._get_pdf_from_ftp_filename(ftp_filename)

        if pdf_path := data.get("pdf_path") or extra.get("pdf_path"):
            return self._get_pdf_from_path(pdf_path)

        raise ValueError("Payload debe contener pdf_base64, pdf_url, ftp_filename o pdf_path")

    def _get_extra_data(self, data: dict) -> dict:
        extra = data.get("extra_data")
        if isinstance(extra, str):
            try:
                extra = json.loads(extra) if extra.strip() else {}
            except json.JSONDecodeError:
                extra = {}
        return extra if isinstance(extra, dict) else {}

    def _get_pdf_from_ftp_filename(self, filename: str) -> bytes:
        s3_base = os.getenv("S3_REMITOS_FRIC_ROT_BASE_URL", "").rstrip("/")
        if s3_base:
            url = f"{s3_base}/{filename.lstrip('/')}"
            return self._download_pdf(url)

        path = Path(filename)
        full_path = path if path.is_absolute() else Path("/app/infrastructure/data/pdfs") / path

        if full_path.exists():
            return full_path.read_bytes()

        raise FileNotFoundError(f"PDF no encontrado: {full_path}")

    def _get_pdf_from_path(self, pdf_path: str) -> bytes:
        path = Path(pdf_path)
        full_path = path if path.is_absolute() else Path("/app/infrastructure/data/pdfs") / path

        if not full_path.exists():
            raise FileNotFoundError(f"PDF no encontrado: {full_path}")

        return full_path.read_bytes()

    def _download_pdf(self, url: str) -> bytes:
        with httpx.Client() as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.content
