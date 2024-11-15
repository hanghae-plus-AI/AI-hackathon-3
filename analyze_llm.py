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
from pdf_analyze import PDFLoader
from schemas.response import ResumeInfoResponse
from langchain.schema import Document

import json
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

refine_prompt = ChatPromptTemplate.from_messages([
    
    (
        "system",
        "이력서에서 주요 정보를 추출하여 다음 데이터 구조에 맞게 정보를 찾아줘\n",
    ),
    (
        "system",
        "Data Structure:\n"
        "\n### ResumeInfo\n"
        "- resume_id: INTEGER\n"
        "- applicant_name: TEXT\n"
        "- job_category: ENUM ('frontend', 'backend', 'ai', 'fullstack')\n"
        "- years: ENUM ('0-3', '3-7', '7-10')\n"
        "- language: ENUM ('python', 'java', 'javascript', 'typescript', 'kotlin', 'c++', 'c' 중 하나)\n"
    ),
    (
        "system",
        "답변은 반드시 다음 JSON 형식을 지켜서 작성해줘\n",
    ),
    (
        "system",
        "Response Dictionary:\n"
        "{{\n"
        '    "resume_id": int,  // 이력서 ID\n'
        '    "applicant_name": str,  // 지원자 이름\n'
        '    "job_category": str,  // 직무 분야 ("frontend", "backend", "ai", "fullstack")\n'
        '    "years": str,  // 경력 연차 ("0-3", "3-7", "7-10")\n'
        '    "language": str  // 주력 프로그래밍 언어 ("python", "java", "javascript", "typescript", "kotlin", "c++", "c" 중 하나)\n'
        "}}\n",
    ),
    (
        "human",
        "Resume:\n{question}\n",
    ),
])

refine_llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-4o-mini",
    callbacks=[
        LogCallbackHandler("refine json"),
    ],
)

refine_llm_with_schema = refine_llm.with_structured_output(ResumeInfoResponse)


def pdf_to_documents(documents: list[Document]):

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


if __name__ == "__main__":
    
    file_path = "./pdf_data/backend_추만석.pdf"

    pdf_loader = PDFLoader(storage_type="local")
    pdf_data = pdf_loader.load_pdf(file_path)

    response = pdf_to_documents(pdf_data)
    json_response = json.loads(response)
    print(json_response)