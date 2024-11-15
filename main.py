from fastapi import FastAPI, APIRouter

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from schemas.request import ResumeRecommendRequest, AnalyzeResumeRequest
from schemas.response import InterviewQuestionResponse, ResumeInfoResponse
from schemas.enums import QuestionType, JobCategory, YearsOfExperience, ProgrammingLanguage

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

ai_router = APIRouter(
    prefix='/api/ai',
    tags = ['AI'],
    responses={404: {"description": "Not found"}},
)

@ai_router.post('/resumes-chat',
                summary="질문을 기반으로 적합한 이력서 추천",
                description="채용담당관의 요구사항을 기반으로 적합한 이력서 추천",
                response_description="",
                )
def resumes_chat(req: ResumeRecommendRequest) -> list[int]:
    return [1]


@ai_router.post('/resumes/{resume_id}/interview',
                summary="이력서를 기반으로 질문 생성",
                description="이력서를 기반으로 질문 생성",
                response_description="질문은 직군별 질문, 컬쳐핏 질문, 경험 질문, 프로젝트 질문으로 나눌 수 있음.",
                )
def interview(resume_id: int) -> list[InterviewQuestionResponse]:
    
    return [InterviewQuestionResponse(question_type=QuestionType.JOB_SPECIFIC, question="[백엔드 직군별 질문]: 네트워크 통신 프로토콜에 대해 설명해주세요."),
            InterviewQuestionResponse(question_type=QuestionType.CULTURE_FIT, question="[컬쳐핏 질문]: 팀원들과 협업하는 방법에 대해 설명해주세요."),
            InterviewQuestionResponse(question_type=QuestionType.EXPERIENCE, question="[경험 질문]: 최근 프로젝트에서 가장 어려웠던 부분은 무엇인가요?"),
            InterviewQuestionResponse(question_type=QuestionType.PROJECT, question="[프로젝트 질문]: 프로젝트 기획 및 설계 과정에 대해 설명해주세요.")]

@ai_router.post('/analyze',
                summary="전달받은 이력서를 전처리(PDF->텍스트)하고, 필요한 정보 추출함",
                description="이력서 업로드 시점에 백그라운드로 실행 예정",
                response_description="",)
def analyze(req: AnalyzeResumeRequest) -> ResumeInfoResponse:
    
    # file_path에서 PDF 읽기: pdf_data = read_pdf(file_path)
    # PDF 전처리 preprocessed_pdf_data = preprocess_pdf(pdf_data)
    # PDF 분석 llm_analyze(preprocessed_pdf_data)

    return ResumeInfoResponse(resume_id=req.resume_id, 
                              applicant_name='김항해', 
                              job_category=JobCategory.FRONTEND, 
                              years=YearsOfExperience.JUNIOR, 
                              language=ProgrammingLanguage.PYTHON)

@ai_router.get('/healthcheck')
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
