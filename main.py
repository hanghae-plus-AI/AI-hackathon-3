from fastapi import FastAPI, APIRouter
from langchain_openai import ChatOpenAI
from vector_store import VectorStoreManager
from pdf_analyze import PDFLoader
from analyze_llm import pdf_to_documents
from dotenv import load_dotenv

load_dotenv()

from schemas.request import ResumeRecommendRequest, AnalyzeResumeRequest
from schemas.response import RecommendedResumeResponse, ResumeInfoResponse, InterviewQuestionResponse
from schemas.enums import QuestionType
from schemas.response import InterviewQuestionResponse, ResumeInfoResponse
from schemas.enums import (
    QuestionType,
    JobCategory,
    YearsOfExperience,
    ProgrammingLanguage,
)

from langchain_openai import ChatOpenAI
from vector_store import save_doc, get_doc_by_id
from dotenv import load_dotenv
from langchain_core.documents import Document
from analize_llm import pdf_to_documents

load_dotenv()

app = FastAPI()
app.pdf_loader = PDFLoader(storage_type="local")
app.vector_store = VectorStoreManager(persist_directory="chroma_wang")

ai_router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
    responses={404: {"description": "Not found"}},
)

@ai_router.post('/resumes-chat',
                summary="질문을 기반으로 적합한 이력서 추천",
                description="채용담당관의 요구사항을 기반으로 적합한 이력서 추천",
                response_description="",
                )
def resumes_chat(req: ResumeRecommendRequest) -> list[RecommendedResumeResponse]:
    return RecommendedResumeResponse(resume_id=1, applicant_name="홍길동", job_category='backend', years='0-3', language='python')


@ai_router.post(
    "/resumes/{resume_id}/interview",
    summary="이력서를 기반으로 질문 생성",
    description="이력서를 기반으로 질문 생성",
    response_description="질문은 직군별 질문, 컬쳐핏 질문, 경험 질문, 프로젝트 질문으로 나눌 수 있음.",
)
def interview(resume_id: int) -> list[InterviewQuestionResponse]:
    # resume_id에 해당하는 정보 chroma db에서 가져오기
    # resume_info = app.vector_store.get_resume_info(resume_id) 

    return [
        InterviewQuestionResponse(
            question_type=QuestionType.JOB_SPECIFIC,
            question="[백엔드 직군별 질문]: 네트워크 통신 프로토콜에 대해 설명해주세요.",
        ),
        InterviewQuestionResponse(
            question_type=QuestionType.CULTURE_FIT,
            question="[컬쳐핏 질문]: 팀원들과 협업하는 방법에 대해 설명해주세요.",
        ),
        InterviewQuestionResponse(
            question_type=QuestionType.EXPERIENCE,
            question="[경험 질문]: 최근 프로젝트에서 가장 어려웠던 부분은 무엇인가요?",
        ),
        InterviewQuestionResponse(
            question_type=QuestionType.PROJECT,
            question="[프로젝트 질문]: 프로젝트 기획 및 설계 과정에 대해 설명해주세요.",
        ),
    ]


@ai_router.post(
    "/analyze",
    summary="전달받은 이력서를 전처리(PDF->텍스트)하고, 필요한 정보 추출함",
    description="이력서 업로드 시점에 백그라운드로 실행 예정",
    response_description="",
)
def analyze(req: AnalyzeResumeRequest) -> ResumeInfoResponse:

    # file_path에서 PDF 읽기: pdf_data = load_pdf(req.file_path)
    pdf_data = app.pdf_loader.load_pdf(req.file_path)
    # PDF 전처리 preprocessed_pdf_data = preprocess_pdf(pdf_data)
    # PDF 분석 llm_analyze(preprocessed_pdf_data)
    analyzed_data = pdf_to_documents(pdf_data)

    # chroma db에 저장
    app.vector_store.add_resume(content=pdf_data, 
                                resume_id=req.resume_id, 
                                applicant_name=analyzed_data.applicant_name, 
                                job_category=analyzed_data.job_category, 
                                years=analyzed_data.years, 
                                language=analyzed_data.language)

    return ResumeInfoResponse(
        resume_id=req.resume_id,
        applicant_name=analyzed_data.applicant_name,
        job_category=analyzed_data.job_category,
        years=analyzed_data.years,
        language=analyzed_data.language,
    )


@ai_router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


app.include_router(ai_router)


@ai_router.get("/llm")
def check_llm():
    llm = ChatOpenAI(
        temperature=0.1,
        model="gpt-4o-mini",
    )
    response = llm.invoke("test")
    return {"message": response.content}


@ai_router.get("/llm")
def check_llm():
    llm = ChatOpenAI(
        temperature=0.1,
        model="gpt-4o-mini",
    )
    response = llm.invoke("test")
    return {"message": response.content}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
