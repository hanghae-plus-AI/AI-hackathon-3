from langchain.document_loaders import PyPDFLoader
import enum
import tempfile
import os

class StorageType(enum.Enum):
    LOCAL = "local"
    S3 = "s3"

class Storage:
    storage_type: StorageType
    file_path: str


class PDFLoader:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.handler = {'local': self._load_local_pdf, 
                        's3': self._load_s3_pdf}

    def load_pdf(self) -> str:
        """로컬 PDF 파일 로드"""
        return self.handler[self.storage.storage_type](self.storage.file_path)
    

    def _load_local_pdf(self, file_path: str) -> str:
        if not os.path.exists(self.storage.file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        loader = PyPDFLoader(file_path)
        return loader.load()

    def _load_s3_pdf(self, bucket_name: str, file_path: str) -> List[str]:
        """S3에서 PDF 파일 로드"""
        if not hasattr(self, 's3_client'):
            raise ValueError("AWS credentials not provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            try:
                self.s3_client.download_file(bucket_name, file_path, temp_file.name)
                loader = PyPDFLoader(temp_file.name)
                return loader.load()
            finally:
                os.unlink(temp_file.name)
    

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