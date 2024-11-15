from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnableMap, RunnableParallel, RunnablePassthrough
from langchain.chains.openai_functions import create_structured_output_chain
from dotenv import load_dotenv
from LogCallbackHandler import LogCallbackHandler
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

summarize_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "이력서 정보를 요약해주는 전문가야\n" "이력서의 요점을 요약해줘 \n",
        ),
        (
            "human",
            "Resume : \n{question}\n",
        ),
    ],
)

summarize_llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-4o-mini",
    callbacks=[
        LogCallbackHandler("summarize resume"),
    ],
)


# Output schema 정의 (Pydantic BaseModel 사용)
class Qualification(BaseModel):
    name: str  # 자격증 이름
    score: int  # 점수


class UserProfile(BaseModel):
    career: int  # 경력
    education_level: int  # 학력 수준
    qualifications: List[Qualification]  # 자격증 리스트
    domains: List[str]  # 전문 분야
    competences: List[str]  # 주요 역량


refine_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "주요정보를 추출해줄거야 다음 Data structure 에 맞는 데이터를 찾아줘\n",
        ),
        (
            "system",
            "Data Structure:\n"
            "\n### ResumeInfoResponse(BaseModel)\n"
            "- resume_id: INTEGER PRIMARY KEY\n"
            "- applicant_name: INTEGER\n"
            "- job_category: JobCategory #Enum\n"
            "- years: YearsOfExperience #Enum\n"
            "- language: ProgrammingLanguage #Enum\n"
            "\n### JobCategory(enum.Enum)\n"
            "- FRONTEND\n"
            "- BACKEND\n"
            "- AI\n"
            "- FULLSTACK\n"
            "\n### YearsOfExperience(enum.Enum)\n"
            "- JUNIOR = '0-3'  # 주니어\n"
            "- MIDLEVEL = '3-7'  # 미들\n"
            "- SENIOR = '7-1'  # 시니어\n"
            "\n### ProgrammingLanguage(enum.Enum)\n"
            "- PYTHON = 'python'\n"
            "- JAVA = 'java'\n"
            "- JAVASCRIPT = 'javascript'\n"
            "- TYPESCRIPT = 'typescript'\n"
            "- KOTLIN = 'kotlin'\n"
            "- CPLUSPLUS = '++'\n"
            "- C = 'c'\n",
        ),
        (
            "human",
            "Resume : \n{question}\n",
        ),
    ],
)

refine_llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-4o-mini",
    callbacks=[
        LogCallbackHandler("refine json"),
    ],
)

refine_llm_with_schema = refine_llm.with_structured_output(UserProfile)


def pdf_to_documents(pdf_path):

    # PDF 로더를 사용하여 파일 읽기
    loader = PyPDFLoader(pdf_path)

    # Document 객체 리스트로 변환
    documents = loader.load()

    resume = ""
    for doc in documents:
        resume += doc.page_content
    response = (
        RunnableParallel(
            question=(summarize_prompt | summarize_llm | (lambda x: x.content))
        )
        | refine_prompt
        | refine_llm_with_schema
    ).invoke(resume)
    print(response)


if __name__ == "__main__":
    pdf_to_documents("./pdf_data/backend_추만석.pdf")
