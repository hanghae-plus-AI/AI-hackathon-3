from pydantic import BaseModel
from uuid import UUID
from .enums import QuestionType, JobCategory, YearsOfExperience, ProgrammingLanguage

class RecommendedResumeResponse(BaseModel):
    resume_id: UUID
    applicant_name: str
    job_category: JobCategory
    years: YearsOfExperience
    language: ProgrammingLanguage


class InterviewQuestionResponse(BaseModel):
    question_type: QuestionType
    question: str


class ResumeInfoResponse(BaseModel):
    resume_id: UUID
    applicant_name: str
    job_category: JobCategory
    years: YearsOfExperience
    language: ProgrammingLanguage


class ResumeFilter(BaseModel):
    applicant_name: str | None
    job_category: JobCategory | None
    years: YearsOfExperience | None
    language: ProgrammingLanguage | None
