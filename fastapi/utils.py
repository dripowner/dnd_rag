import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


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
