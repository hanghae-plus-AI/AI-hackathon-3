from pydantic import BaseModel
from .enums import QuestionType, JobCategory, YearsOfExperience, ProgrammingLanguage


class InterviewQuestionResponse(BaseModel):
    question_type: QuestionType
    question: str


class ResumeInfoResponse(BaseModel):
    resume_id: int
    applicant_name: str
    job_category: JobCategory
    years: YearsOfExperience
    language: ProgrammingLanguage

