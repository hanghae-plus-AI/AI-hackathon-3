from fastapi import FastAPI, APIRouter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

ai_router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    responses={404: {"description": "Not found"}},
)


@ai_router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


app.include_router(ai_router)


@ai_router.get("/llm")
def check_llm():
    llm = ChatOpenAI(
        temperature=0.1,
        model="gpt-4o-mini",
    )
    response = llm.invoke("test")
    return {"message": response.content}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
