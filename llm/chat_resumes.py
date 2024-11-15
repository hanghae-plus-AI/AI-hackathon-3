from llm.vector_store import VectorStoreManager
from schemas.request import ResumeRecommendRequest

vector_store = VectorStoreManager(persist_directory="chroma_wang").vector_store


def chat_resumes_retrieval(req: ResumeRecommendRequest):
    return vector_store.similarity_search(req.message, k=5)
