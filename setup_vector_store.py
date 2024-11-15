from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

docs = [
    Document(
        page_content=f"""
            test
        """,
        metadata={},
    )
]

vector_store = Chroma.from_documents(docs, embeddings, persist_directory="chroma_wang")
vector_store.persist()
