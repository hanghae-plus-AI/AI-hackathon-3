from pydantic import BaseModel
from .enums import QuestionType, JobCategory, YearsOfExperience, ProgrammingLanguage


class InterviewQuestionResponse(BaseModel):
    question_type: QuestionType
    question: str


class ResumeInfoResponse(BaseModel):
    """
    이력서 정보 응답 (ResumeInfoResponse)

    지원자의 주요 이력서 정보를 포함하는 데이터 클래스.
    """

    resume_id: int
    applicant_name: str
    job_category: JobCategory
    years: YearsOfExperience
    language: ProgrammingLanguage
