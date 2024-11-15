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
from schemas.response import ResumeInfoResponse

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

refine_llm_with_schema = refine_llm.with_structured_output(ResumeInfoResponse)


def generate_question(resume):

    pass


if __name__ == "__main__":
    pass
