import enum

class QuestionType(enum.Enum):
    JOB_SPECIFIC = "직군별 질문"
    CULTURE_FIT = "컬쳐핏 질문"
    EXPERIENCE = "경험 질문"
    PROJECT = "프로젝트 질문"

    def __str__(self) -> str:
        return self.value

class JobCategory(enum.Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    AI = "ai"
    FULLSTACK = "fullstack"

    def __str__(self) -> str:
        return self.value


class YearsOfExperience(enum.Enum):
    JUNIOR = "0-3"             # 주니어
    MIDLEVEL = "3-7"           # 미들
    SENIOR = "7-10"            # 시니어
    
    @classmethod
    def list(cls) -> list[str]:
        return [years.value for years in cls]
    
    def __str__(self) -> str:
        return self.value


class ProgrammingLanguage(enum.Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    KOTLIN = "kotlin"
    CPLUSPLUS = "c++"
    C = "c"

    def __str__(self) -> str:
        return self.value
