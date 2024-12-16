import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_documents(data_folder_path: str) -> list[Document]:
    pdfs = [f for f in os.listdir(data_folder_path) if f.endswith(".pdf")]
    documents = []
    for pdf in pdfs:
        loader = PyPDFLoader(os.path.join(data_folder_path, pdf))
        documents.extend(loader.load())

    return documents
