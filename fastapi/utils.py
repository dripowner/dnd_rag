import os

from langchain.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_core.runnables import Runnable
from langsmith import traceable
from schemes import Message


def load_documents(data_folder_path: str) -> list[Document]:
    files = [
        f
        for f in os.listdir(data_folder_path)
        if f.endswith(".pdf") or f.endswith(".txt")
    ]
    documents = []
    for file in files:
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(data_folder_path, file))
        else:
            loader = TextLoader(os.path.join(data_folder_path, file))
        documents.extend(loader.load())

    return documents


@traceable(project_name=os.getenv("LANGCHAIN_PROJECT"))
def get_answer(
    query: Message, retrieval_qa: Runnable, memory: ConversationBufferWindowMemory
):
    response = retrieval_qa.invoke(
        {
            "input": query.message,
            "chat_history": memory.load_memory_variables({})["chat_history"],
        }
    )
    memory.save_context({"input": query.message}, {"output": response["answer"]})
    return response
