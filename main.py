from fastapi import FastAPI, APIRouter, BackgroundTasks
from langchain_openai import ChatOpenAI
from llm.vector_store import VectorStoreManager
from pdf_analyze import PDFLoader
from llm.analyze import pdf_to_documents
from dotenv import load_dotenv


from schemas.request import ResumeRecommendRequest, AnalyzeResumeRequest
from schemas.response import (
    RecommendedResumeResponse,
    ResumeInfoResponse,
    InterviewQuestionResponse,
)


from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from llm.generate_question import generate_question
from llm.chat_resumes import chat_resumes_retrieval

load_dotenv()

app = FastAPI()
app.pdf_loader = PDFLoader(storage_type="s3")
app.vector_store = VectorStoreManager(persist_directory="chroma_wang")

ai_router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
    responses={404: {"description": "Not found"}},
)


async def write_to_vector_db(
    content, resume_id, applicant_name, job_category, years, language
):
    app.vector_store.add_resume(
        content=content,
        resume_id=resume_id,
        applicant_name=applicant_name,
        job_category=job_category,
        years=years,
        language=language,
    )


@ai_router.post(
    "/resumes-chat",
    summary="질문을 기반으로 적합한 이력서 추천",
    description="채용담당관의 요구사항을 기반으로 적합한 이력서 추천",
    response_description="",
)
def resumes_chat(req: ResumeRecommendRequest) -> list[RecommendedResumeResponse]:
    return chat_resumes_retrieval(req)


@ai_router.post(
    "/resumes/{resume_id}/interview",
    summary="이력서를 기반으로 질문 생성",
    description="이력서를 기반으로 질문 생성",
    response_description="질문은 직군별 질문, 컬쳐핏 질문, 경험 질문, 프로젝트 질문으로 나눌 수 있음.",
)
def interview(resume_id: int) -> list[InterviewQuestionResponse]:
    # resume_id에 해당하는 정보 chroma db에서 가져오기
    resume_info = app.vector_store.get_resume_info(resume_id)

    from llm.generate_question import generate_question

    questions = generate_question("".join(resume_info["documents"]))

    return questions


@ai_router.post(
    "/analyze",
    summary="전달받은 이력서를 전처리(PDF->텍스트)하고, 필요한 정보 추출함",
    description="이력서 업로드 시점에 백그라운드로 실행 예정",
    response_description="",
)
def analyze(
    req: AnalyzeResumeRequest, background_tasks: BackgroundTasks
) -> ResumeInfoResponse:
    pdf_data = app.pdf_loader.load_pdf(req.file_path)
    analyzed_data = pdf_to_documents(pdf_data)

    background_tasks.add_task(
        write_to_vector_db,
        analyzed_data["summary"],
        req.resume_id,
        analyzed_data["resume_info"].applicant_name,
        analyzed_data["resume_info"].job_category,
        analyzed_data["resume_info"].years,
        analyzed_data["resume_info"].language,
    )

    return ResumeInfoResponse(
        resume_id=req.resume_id,
        applicant_name=analyzed_data["resume_info"].applicant_name,
        job_category=analyzed_data["resume_info"].job_category,
        years=analyzed_data["resume_info"].years,
        language=analyzed_data["resume_info"].language,
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
