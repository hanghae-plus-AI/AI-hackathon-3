from langchain.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "Example conversation Starts"),
        (
            "human",
            """
            Resume :
            - id: 1
            - user_id: 101
            - career: 5
            - applicant_name: 홍길동
            - education_level: 4
            - qualifications:
            - name: "TOEIC 점수"
            - score: 900
            - name: "OPIC 점수"
            - score: 5
            - domains:
            - "AI"
            - "Data Science"
            - competences:
            - "Problem Solving"
            - "Communication
            """,
        ),
        (
            "assistant",
            """{
            "career": 5,
            "education_level": 4,
            "qualifications": [
                {
                    "name": "TOEIC 점수",
                    "score": 900
                },
                {
                    "name": "OPIC 점수",
                    "score": 5
                }
            ],
            "domains": ["AI", "Data Science"],
            "competences": ["Problem Solving", "Communication"]
        }""",
        ),
        ("system", "Example conversation Ends"),
        (
            "system",
            """
            Response Json:
            { 
                "career": int,  // 경력 (숫자 입력, 예: 3)
                "education_level": int,  // 학력 수준 (1: 초졸, 2: 중졸, 3: 고졸, 4: 대졸, 5: 석사, 6: 박사 중 숫자 입력)
                "qualifications": list({
                    "name": str,  // 자격증 이름 ('TOEIC 점수' or 'TOEFL 점수' or 'OPIC 점수' or 'TOEIC_SPEAKING 점수' or 'TEPS 점수'only)
                    "score": int  // 점수 (OPIC 인 경우 1~6 중 숫자 입력, OPIC: IL(1), IM 1(2), IM 2(3), IM 3(4), IH(5), AL(6))
                }),
                "domains": list(str),  // 전문 분야 (예: "AI", "Data Science")
                "competences": list(str)  // 주요 역량 (예: "Problem Solving", "Communication")
            }
            """,
        ),
        (
            "system",
            "이력서 정보를 분석해주는 전문가야\n"
            "Data Structure 를 참고해서 DB에 넣을 수 있는 데이터가 있다면 추출해줘\n"
            "답변은 Response Json 의 형식을 엄격하게 지켜야해 \n",
        ),
        (
            "human",
            "Resume : {question}\n",
        ),
    ],
)

llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-4o-mini",
)


def pdf_to_documents(pdf_path):

    # PDF 로더를 사용하여 파일 읽기
    loader = PyPDFLoader(pdf_path)

    # Document 객체 리스트로 변환
    documents = loader.load()

    for doc in documents:
        response = llm.invoke(doc.page_content)
        print(response.content)


if __name__ == "__main__":
    pdf_to_documents("./pdf_data/backend_문정환.pdf")
