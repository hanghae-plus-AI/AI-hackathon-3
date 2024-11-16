import enum
import os

from PyPDF2 import PdfReader
from io import BytesIO
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
import boto3

class StorageType(enum.Enum):
    LOCAL = "local"
    S3 = "s3"


class PDFLoader:
    def __init__(self, storage_type: StorageType):
        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                      region_name=os.getenv('AWS_REGION'))
        
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        self.storage_type = storage_type
        self.handler = {'local': self._load_local_pdf, 
                        's3': self._load_s3_pdf}

    def load_pdf(self, file_path: str) -> list[Document]:
        """로컬 PDF 파일 로드"""
        return self.handler[self.storage_type](file_path)
    
    def _load_local_pdf(self, file_path: str) -> list[Document]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        pdf_reader = PdfReader(file_path)
        documents = []
        
        for page in pdf_reader.pages:
            documents.append(
                Document(
                    page_content=page.extract_text(),
                    metadata={'source': file_path}
                )
            )
    
        return documents

    def _load_s3_pdf(self, file_path: str) -> list[Document]:
        if not hasattr(self, 's3_client'):
            raise ValueError("AWS credentials not provided")
        
        
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=file_path
        )
        
        pdf_stream = BytesIO(response['Body'].read())
        pdf_reader = PdfReader(pdf_stream)
        documents = []
        
        for page in pdf_reader.pages:
            documents.append(
                Document(
                    page_content=page.extract_text(),
                    metadata={'source': f"s3://{self.bucket_name}/{file_path}"}
                )
            )
        
        return documents

def load_pdf(file_path: str) -> str:
    '''
    PDF 파일을 저장소에서 읽어오기
    '''
    pass

def preprocess_pdf(pdf_data: str) -> str:
    '''
    PDF 텍스트를 전처리하여 필요한 정보 추출
    '''
    pass

def llm_analyze(pdf_data: str) -> str:
    '''
    PDF 텍스트를 분석하여 필요한 정보 추출
    '''
    pass