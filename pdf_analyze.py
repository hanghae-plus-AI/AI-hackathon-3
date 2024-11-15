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
    

    def _load_local_pdf(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        loader = PyPDFLoader(file_path)
        return loader.load()

    def _load_s3_pdf(self, bucket_name: str, file_path: str) -> list[str]:
        """S3에서 PDF 파일을 스트림으로 로드"""
        if not hasattr(self, 's3_client'):
            raise ValueError("AWS credentials not provided")
        
        try:
            # S3에서 파일 객체 가져오기
            response = self.s3_client.get_object(
                Bucket=bucket_name,
                Key=file_path
            )
            
            # 스트림으로 읽기
            pdf_stream = BytesIO(response['Body'].read())
            
            # PyPDF2로 직접 처리
            pdf_reader = PdfReader(pdf_stream)
            texts = []
            
            for page in pdf_reader.pages:
                texts.append({
                    'page_content': page.extract_text(),
                    'metadata': {'source': f"s3://{bucket_name}/{file_path}"}
                })
            
            return texts
            
        except Exception as e:
            raise Exception(f"Error reading PDF from S3: {str(e)}")

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