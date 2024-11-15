import enum


class QuestionType(enum.Enum):
    JOB_SPECIFIC = "직군별 질문"
    CULTURE_FIT = "컬쳐핏 질문"
    EXPERIENCE = "경험 질문"
    PROJECT = "프로젝트 질문"

    def __str__(self) -> str:
        return self.value


class JobCategory(enum.Enum):
    """
    직무 카테고리 (JobCategory)

    직무의 유형을 나타내는 열거형(enum) 클래스.
    """

    FRONTEND = "frontend"
    BACKEND = "backend"
    AI = "ai"
    FULLSTACK = "fullstack"

    def __str__(self) -> str:
        """
        JobCategory 값을 문자열로 변환.
        """
        return self.value


class YearsOfExperience(enum.Enum):
    """
    경력 연차 (YearsOfExperience)

    지원자의 경력 수준을 나타내는 열거형(enum) 클래스.
    """

    JUNIOR = "0-3"  # 주니어
    MIDLEVEL = "3-7"  # 미들
    SENIOR = "7-10"  # 시니어

    @classmethod
    def list(cls) -> list[str]:
        """
        모든 경력 연차 값을 리스트 형태로 반환.
        """
        return [years.value for years in cls]

    def __str__(self) -> str:
        """
        YearsOfExperience 값을 문자열로 변환.
        """
        return self.value


class ProgrammingLanguage(enum.Enum):
    """
    프로그래밍 언어 (ProgrammingLanguage)

    지원자가 사용하는 프로그래밍 언어를 나타내는 열거형(enum) 클래스.
    """

    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    KOTLIN = "kotlin"
    CPLUSPLUS = "c++"
    C = "c"

    def __str__(self) -> str:
        """
        ProgrammingLanguage 값을 문자열로 변환.
        """
        return self.value
