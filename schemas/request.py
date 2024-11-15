from pydantic import BaseModel

class ResumeRecommendRequest(BaseModel):
    message: str

class AnalyzeResumeRequest(BaseModel):
    user_id: str
    resume_id: int
    file_path: str
