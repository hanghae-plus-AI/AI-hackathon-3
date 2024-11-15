import pytest
from fastapi.testclient import TestClient
from main import app
from pdf_analyze import PDFLoader
from langchain.schema import Document

@pytest.fixture
def client():
    return TestClient(app)

def test_load_pdf():
    pdf_loader = PDFLoader(storage_type='local')
    pdf_data = pdf_loader.load_pdf('test.pdf')

    assert isinstance(pdf_data, list)
    assert isinstance(pdf_data[0], Document)