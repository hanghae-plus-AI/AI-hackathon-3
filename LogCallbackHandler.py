import os
from langchain.callbacks.base import BaseCallbackHandler
import csv
from datetime import datetime
from langchain_core.outputs.chat_generation import ChatGeneration
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import toml


class LogCallbackHandler(BaseCallbackHandler):
    """
    이 클래스는 LangChain의 콜백 핸들러로서, LLM(언어 모델)의 상호작용을 로깅하고 토큰 사용량을 기반으로 비용을 계산합니다.
    생성된 대화 내용과 관련 정보를 CSV 파일(qna_log.csv)에 저장합니다.

    사용법:
        handler = LogCallbackHandler()
        # LLM이나 체인에 콜백 핸들러로 추가하여 사용합니다.
    """

    def __init__(self, name):
        # 다양한 모델의 토큰 사용 비용을 계산하기 위한 가격표
        self.price_table = {
            "gpt-4o-mini-2024-07-18": {
                "divider": 1e9,
                "input_tokens": 150,
                "output_tokens": 600,
                "input_token_detail_cache_read": 75,
            }
        }
        self.model_name = name
        # 로그 정보를 저장할 딕셔너리
        self.log_dict = {
            "일시": "",  # 타임스탬프
            "버전": "",  # 프로젝트 버전
            "이름": "",  # 식별하기 위한 이름
            "질의": "",  # 사용자 질문
            "답변": "",  # 모델의 응답
            "첫토큰시간": "",  # 첫 토큰 생성까지 걸린 시간
            "총생성시간": "",  # 전체 응답 생성 시간
            "모델명": "",  # 사용된 모델 이름
            "전체비용": "",  # 토큰 사용량에 따른 총 비용
            "입력토큰": "",  # 입력 토큰 수
            "입력토큰캐시됨": "",  # 캐시된 입력 토큰 수
            "출력토큰": "",  # 출력 토큰 수
            "전체토큰": "",  # 전체 토큰 수
        }
        # 시작 시간과 첫 토큰 생성 시간을 추적하기 위한 변수
        self.start_time = None
        self.first_token_time = None

    def on_chat_model_start(self, serialized, messages, **kwargs):
        # 메시지에서 질문을 추출하여 기록
        self.log_dict["질의"] = messages[0][-1].content.replace("\n", "\\n")
        # 모델이 처리를 시작한 시간을 기록
        self.start_time = datetime.now()

    def on_llm_new_token(self, token, *args, **kwargs):
        # 첫 번째 토큰이 생성된 시간을 기록
        if self.first_token_time is None:  # 첫 토큰만 기록
            self.log_dict["일시"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.first_token_time = datetime.now()
            elapsed_time_to_start = (
                self.first_token_time - self.start_time
            ).total_seconds()
            self.log_dict["첫토큰시간"] = f"{elapsed_time_to_start:.2f}"

    def on_llm_end(self, response, *args, **kwargs):
        self.log_dict["버전"] = self.get_version_from_pyproject()
        self.log_dict["이름"] = self.model_name

        # 응답에서 메시지와 사용량 메타데이터를 추출
        message = response.generations[0][0].message
        model_name = message.response_metadata["model_name"]
        input_tokens = message.usage_metadata["input_tokens"]
        input_token_detail_cache_read = message.usage_metadata["input_token_details"][
            "cache_read"
        ]
        output_tokens = message.usage_metadata["output_tokens"]

        # 메시지에서 답변을 추출하여 기록
        self.log_dict["답변"] = message.content.replace("\n", "\\n")
        # 전체 생성 시간을 계산하여 기록
        self.log_dict["총생성시간"] = (
            f"{(datetime.now() - self.start_time).total_seconds():.2f}"
        )
        # 사용된 모델 이름을 기록
        self.log_dict["모델명"] = model_name
        # 토큰 사용량을 기반으로 총 비용을 계산하여 기록
        self.log_dict["전체비용"] = self.calculate_token_usage_cost(
            input_tokens,
            input_token_detail_cache_read,
            output_tokens,
            model_name,
        )
        # 토큰 사용량 상세 정보를 기록
        self.log_dict["입력토큰"] = input_tokens
        self.log_dict["입력토큰캐시됨"] = input_token_detail_cache_read
        self.log_dict["출력토큰"] = output_tokens
        self.log_dict["전체토큰"] = message.usage_metadata["total_tokens"]

        # 로그 정보를 CSV 파일에 저장
        self.save_message_to_csv()
        self.save_message_to_google_sheet()
        # 다음 상호작용을 위해 로그 딕셔너리와 시간 변수 초기화
        self.init_log_dict()

    def save_message_to_csv(self):
        try:
            file_path = "qna_log.csv"
            file_exists = os.path.isfile(file_path)

            with open(file_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(self.log_dict.keys())
                writer.writerow(self.log_dict.values())
        except Exception as e:
            print(f"CSV 저장 중 오류 발생: {e}")

    def save_message_to_google_sheet(self):
        try:
            # 서비스 계정 인증
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "./log-llm-3316e43cc23b.json", scope
            )

            client = gspread.authorize(creds)

            # 스프레드시트 및 첫 번째 시트 열기
            spreadsheet = client.open("AI_질문답변로그")
            worksheet = spreadsheet.get_worksheet(0)  # 첫 번째 시트

            # 헤더 추가
            if not worksheet.row_values(1):  # 첫 번째 행이 비어 있는 경우
                header = list(self.log_dict.keys())
                worksheet.append_row(header)

            # 데이터 추가
            worksheet.append_row(list(self.log_dict.values()))
        except Exception as e:
            print(f"Google Sheet 저장 중 오류 발생: {e}")

    def get_version_from_pyproject(self, file_path="pyproject.toml"):
        try:
            # pyproject.toml 파일 읽기
            with open(file_path, "r", encoding="utf-8") as file:
                pyproject_data = toml.load(file)

            # 버전 정보 추출
            version = pyproject_data.get("tool", {}).get("poetry", {}).get("version")
            if version:
                return version
            else:
                raise KeyError("Version 정보가 pyproject.toml에 없습니다.")
        except FileNotFoundError:
            raise FileNotFoundError(f"'{file_path}' 파일을 찾을 수 없습니다.")
        except Exception as e:
            raise RuntimeError(f"버전 정보를 읽는 중 오류 발생: {e}")

    def calculate_token_usage_cost(
        self,
        input_tokens,
        input_token_detail_cache_read,
        output_tokens,
        model_name,
    ):
        # 캐시되지 않은 입력 토큰 수 계산
        input_not_cached = input_tokens - input_token_detail_cache_read
        # 캐시되지 않은 입력 토큰의 비용 계산
        input_not_cached_cost = (
            input_not_cached * self.price_table[model_name]["input_tokens"]
        )
        # 캐시된 입력 토큰의 비용 계산
        input_cached_cost = (
            input_token_detail_cache_read
            * self.price_table[model_name]["input_token_detail_cache_read"]
        )
        # 출력 토큰의 비용 계산
        output_tokens_cost = (
            output_tokens * self.price_table[model_name]["output_tokens"]
        )
        # 총 비용 계산 및 divider 적용
        total_cost = (
            input_not_cached_cost + input_cached_cost + output_tokens_cost
        ) / self.price_table[model_name]["divider"]
        return total_cost

    def init_log_dict(self):
        # 로그 딕셔너리와 시간 변수 초기화
        self.log_dict = {
            "일시": "",
            "버전": "",
            "이름": "",
            "질의": "",
            "답변": "",
            "첫토큰시간": "",
            "총생성시간": "",
            "모델명": "",
            "전체비용": "",
            "입력토큰": "",
            "입력토큰캐시됨": "",
            "출력토큰": "",
            "전체토큰": "",
        }
        self.start_time = None
        self.first_token_time = None
