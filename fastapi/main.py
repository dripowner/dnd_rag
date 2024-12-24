import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel
from utils import load_documents

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import dotenv

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global llm, embeddings, vector_store, text_splitter, retrieval_qa, memory
    llm = ChatMistralAI(
        model="mistral-large-latest", api_key=os.getenv("MISTRAL_API_KEY")
    )
    embeddings = HuggingFaceEmbeddings(model_name="cointegrated/rubert-tiny2")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    if os.path.exists("_data/vecstore/vector_store.faiss"):
        vector_store = FAISS.load_local(
            "_data/vecstore/vector_store.faiss",
            embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        documents = load_documents("_data/docs")
        split_documents = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(split_documents, embedding=embeddings)
        vector_store.save_local("_data/vecstore/vector_store.faiss")

    system_template = "Ты помощник по настольным играм Dungeons & Dragons. Твоя задача - помогать игрокам и ведущим в различных аспектах игры, \
        включая правила, создание персонажей, описание монстров, заклинания и многое другое. Используй следующую контекстную информацию, \
        чтобы ответить на вопрос. Если в контексте нет ответа, ответь 'Не знаю ответа на вопрос'. \
        Используй максимум три предложения и будь точным но кратким.\n\nИстория диалога: {chat_history}"

    memory = ConversationBufferWindowMemory(
        k=10, memory_key="chat_history", return_messages=True
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("human", """Контекстная информация: {context}\nВопрос: {input}"""),
        ]
    )
    document_chain = create_stuff_documents_chain(llm, qa_prompt)
    retrieval_qa = create_retrieval_chain(vector_store.as_retriever(), document_chain)

    logging.info("Starting up FastAPI application...")

    yield

    logging.info("Shutting down FastAPI application...")
    vector_store.save_local("_data/vecstore/vector_store.faiss")


class Message(BaseModel):
    message: str


app = FastAPI(lifespan=lifespan)


@app.post("/rag_response")
async def rag_response(query: Message):
    response = retrieval_qa.invoke(
        {
            "input": query.message,
            "chat_history": memory.load_memory_variables({})["chat_history"],
        }
    )
    memory.save_context({"input": query.message}, {"output": response["answer"]})

    return JSONResponse(content={"response": response["answer"]})


@app.post("/add_document")
async def add_document(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Not pdf file"})

    temp_path = f"_data/temp/{file.filename}"
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)

    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    loader = PyPDFLoader(temp_path)
    documents = loader.load()
    split_docs = text_splitter.split_documents(documents)
    vector_store.add_documents(split_docs)

    os.remove(temp_path)

    return JSONResponse(content={"status": "success"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
