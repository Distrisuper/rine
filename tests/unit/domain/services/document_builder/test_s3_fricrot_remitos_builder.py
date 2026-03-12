import pytest
import json
import base64
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
from domain.services.document_builder.s3_fricrot_remitos_builder import S3FricRotRemitosBuilder
from domain.value_objects.rendered_document import RenderedDocument

@pytest.fixture
def builder():
    return S3FricRotRemitosBuilder()

@pytest.fixture
def mock_job():
    def _create_job(payload_dict):
        job = MagicMock()
        job.payload = json.dumps(payload_dict)
        return job
    return _create_job

def test_build_from_pdf_base64_direct(builder, mock_job):
    pdf_content = b"fake-pdf-content"
    encoded = base64.b64encode(pdf_content).decode("utf-8")
    job = mock_job({"pdf_base64": encoded})
    
    result = builder.build(job, None)
    
    assert isinstance(result, RenderedDocument)
    assert result.content == pdf_content
    assert result.content_type == "pdf"

def test_build_from_pdf_base64_in_extra_data_dict(builder, mock_job):
    pdf_content = b"fake-pdf-content-extra"
    encoded = base64.b64encode(pdf_content).decode("utf-8")
    job = mock_job({
        "extra_data": {"pdf_base64": encoded}
    })
    
    result = builder.build(job, None)
    
    assert result.content == pdf_content

def test_build_from_pdf_base64_in_extra_data_string(builder, mock_job):
    pdf_content = b"fake-pdf-content-extra-string"
    encoded = base64.b64encode(pdf_content).decode("utf-8")
    job = mock_job({
        "extra_data": json.dumps({"pdf_base64": encoded})
    })
    
    result = builder.build(job, None)
    
    assert result.content == pdf_content

@patch("httpx.Client")
def test_build_from_pdf_url_success(mock_client, builder, mock_job):
    pdf_content = b"downloaded-pdf"
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.get.return_value = MagicMock(content=pdf_content, status_code=200)
    
    job = mock_job({"pdf_url": "http://example.com/file.pdf"})
    
    result = builder.build(job, None)
    
    assert result.content == pdf_content
    mock_instance.get.assert_called_once_with("http://example.com/file.pdf")

@patch("os.getenv")
@patch("httpx.Client")
def test_build_from_ftp_filename_s3(mock_client, mock_getenv, builder, mock_job):
    mock_getenv.return_value = "https://s3.amazonaws.com/bucket"
    pdf_content = b"s3-pdf-content"
    mock_instance = mock_client.return_value.__enter__.return_value
    mock_instance.get.return_value = MagicMock(content=pdf_content, status_code=200)
    
    job = mock_job({"ftp_filename": "remito_123.pdf"})
    
    result = builder.build(job, None)
    
    assert result.content == pdf_content
    mock_instance.get.assert_called_once_with("https://s3.amazonaws.com/bucket/remito_123.pdf")

@patch("os.getenv")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.read_bytes")
def test_build_from_ftp_filename_local_fallback(mock_read, mock_exists, mock_getenv, builder, mock_job):
    mock_getenv.return_value = "" # No S3 URL
    mock_exists.return_value = True
    pdf_content = b"local-pdf-content"
    mock_read.return_value = pdf_content
    
    job = mock_job({"ftp_filename": "local_file.pdf"})
    
    result = builder.build(job, None)
    
    assert result.content == pdf_content
    assert mock_exists.called

@patch("pathlib.Path.exists")
@patch("pathlib.Path.read_bytes")
def test_build_from_pdf_path_success(mock_read, mock_exists, builder, mock_job):
    mock_exists.return_value = True
    pdf_content = b"path-pdf-content"
    mock_read.return_value = pdf_content
    
    job = mock_job({"pdf_path": "/absolute/path/to/file.pdf"})
    
    result = builder.build(job, None)
    
    assert result.content == pdf_content

def test_build_missing_all_sources_error(builder, mock_job):
    job = mock_job({"other_field": "no-pdf-here"})
    
    with pytest.raises(ValueError, match="Payload debe contener pdf_base64, pdf_url, ftp_filename o pdf_path"):
        builder.build(job, None)

@patch("pathlib.Path.exists")
def test_build_pdf_path_not_found_error(mock_exists, builder, mock_job):
    mock_exists.return_value = False
    job = mock_job({"pdf_path": "/non/existent/file.pdf"})
    
    with pytest.raises(FileNotFoundError, match="PDF no encontrado"):
        builder.build(job, None)
