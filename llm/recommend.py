from llm.vector_store import VectorStoreManager
from schemas.request import ResumeRecommendRequest
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Optional, Dict, Any
from schemas.enums import QuestionType, JobCategory, YearsOfExperience, ProgrammingLanguage

class QueryInfoExtractor:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["message"],
            template="""
            다음 메시지에서 이력서 관련 정보를 추출해주세요:
            {message}
            
            다음 형식으로 정확히 답변해주세요:
            job_category: (BACKEND/FRONTEND/FULLSTACK/MOBILE/DATA/AI/DEVOPS 중 하나 또는 NONE)
            years: (JUNIOR/MIDDLE/SENIOR 중 하나 또는 NONE)
            language: (PYTHON/JAVA/JAVASCRIPT/KOTLIN/SWIFT/GO 중 하나 또는 NONE)
            """
        )
        self.chain = LLMChain(llm=llm, prompt=self.prompt)

    def extract(self, message: str) -> Dict[str, Optional[str]]:
        try:
            # LLM으로부터 응답 받기
            response = self.chain.run(message=message)
            
            # 응답 파싱
            result = {}
            for line in response.strip().split('\n'):
                key, value = line.split(': ')
                value = value.strip()
                
                # Enum 매핑
                if key == 'job_category':
                    result[key] = getattr(JobCategory, value) if value != 'NONE' else None
                elif key == 'years':
                    result[key] = getattr(YearsOfExperience, value) if value != 'NONE' else None
                elif key == 'language':
                    result[key] = getattr(ProgrammingLanguage, value) if value != 'NONE' else None
                    
            return result
            
        except Exception as e:
            # 에러 발생시 모든 필드에 None 반환
            return {
                'job_category': None,
                'years': None,
                'language': None
            }

def select_fit_resumes(req: ResumeRecommendRequest, 
                       query_info_extractor: QueryInfoExtractor, 
                       vector_store: VectorStoreManager):
    filter_metadata = query_info_extractor.extract(req.message)
    # req.message를 기반으로 적합한 이력서  0     
    return [doc.metadata for doc in vector_store.search_resumes(req.message, k=5, filter_metadata=filter_metadata)]
