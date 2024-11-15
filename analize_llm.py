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
            "\n### Resume Table\n"
            "- id: INTEGER PRIMARY KEY\n"
            "- user_id: INTEGER\n"
            "- career: INTEGER\n"
            "- applicant_name: TEXT\n"
            "- education_level: INTEGER\n"
            "\n### Qualification Table\n"
            "- id: INTEGER PRIMARY KEY\n"
            "- resume_id: INTEGER (Foreign Key, references Resume(id))\n"
            "- name: TEXT ('TOEIC' or 'TOEFL' only)\n"
            "- score: INTEGER\n"
            "\n### Domain Table\n"
            "- id: INTEGER PRIMARY KEY\n"
            "- resume_id: INTEGER (Foreign Key, references Resume(id))\n"
            "- name: TEXT\n"
            "\n### Competence Table\n"
            "- id: INTEGER PRIMARY KEY\n"
            "- resume_id: INTEGER (Foreign Key, references Resume(id))\n"
            "- name: TEXT\n",
        ),
        (
            "system",
            "답변양식은 다음과 같아야해 반드시 지켜줘\n",
        ),
        (
            "system",
            "Response Json:\n"
            "{{ \n"
            '    "career": int,  // 경력 (숫자 입력, 예: 3)\n'
            '    "education_level": int,  // 학력 수준 (1: 초졸, 2: 중졸, 3: 고졸, 4: 대졸, 5: 석사, 6: 박사 중 숫자 입력)\n'
            '    "qualifications": list({{\n'
            "        \"name\": str,  // 자격증 이름 ('TOEIC 점수' or 'TOEFL 점수' or 'OPIC 점수' or 'TOEIC_SPEAKING 점수' or 'TEPS 점수'only)\n"
            '        "score": int  // 점수 (OPIC 인 경우 1~6 중 숫자 입력, OPIC: IL(1), IM 1(2), IM 2(3), IM 3(4), IH(5), AL(6))\n'
            "    }}),\n"
            '    "domains": list(str),  // 전문 분야 (예: "AI", "Data Science")\n'
            '    "competences": list(str)  // 주요 역량 (예: "Problem Solving", "Communication")\n'
            "}}\n",
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
