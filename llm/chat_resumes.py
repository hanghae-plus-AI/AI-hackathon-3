from llm.vector_store import VectorStoreManager
from schemas.request import ResumeRecommendRequest
from schemas.response import RecommendedResumeResponse

vector_store = VectorStoreManager(persist_directory="chroma_wang").vector_store


def chat_resumes_retrieval(req: ResumeRecommendRequest):
    return [doc.metadata for doc in vector_store.similarity_search(req.message, k=5)]
