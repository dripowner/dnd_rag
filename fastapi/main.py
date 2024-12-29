import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import dotenv
import uvicorn
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import Client
from schemes import Feedback, Message
from utils import get_answer, load_documents

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global llm, embeddings, vector_store, text_splitter, retrieval_qa, memory, ls_client
    ls_client = Client(api_key=os.getenv("LANGCHAIN_API_KEY"))
    llm = ChatMistralAI(
        model="mistral-large-latest", api_key=os.getenv("MISTRAL_API_KEY"), timeout=60
    )
    embeddings = HuggingFaceEmbeddings(model_name="cointegrated/rubert-tiny2")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)

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

    system_template = (
        "Ты помощник по настольным играм Dungeons & Dragons. Твоя задача - помогать игрокам и ведущим в различных аспектах игры, \
        включая правила, создание персонажей, описание монстров, заклинания и многое другое. Также ты должен подробно и точно отвечать на вопросы по сюжету и миру игры. \
        Используй следующую контекстную информацию, чтобы ответить на вопрос. Если в контексте нет ответа, ответь 'Не знаю ответа на вопрос'. \
        <удь точным но кратким.\n\nИстория диалога: {chat_history}"
    )

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


app = FastAPI(lifespan=lifespan)


@app.post("/rag_response")
async def rag_response(query: Message):
    run_id = str(uuid.uuid4())

    response = get_answer(
        query, retrieval_qa, memory, langsmith_extra={"run_id": run_id}
    )

    return JSONResponse(
        content={
            "response": response["answer"],
            "context": [doc.page_content for doc in response["context"]],
            "run_id": run_id,
        }
    )


@app.post("/add_document")
async def add_document(file: UploadFile):
    if not file.filename.endswith((".pdf", ".txt")):
        return JSONResponse(status_code=400, content={"error": "Not pdf or txt file"})

    temp_path = f"_data/temp/{file.filename}"
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)

    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    if file.filename.endswith(".pdf"):
        loader = PyPDFLoader(temp_path)
    else:
        loader = TextLoader(temp_path)
    documents = loader.load_and_split(text_splitter)
    vector_store.add_documents(documents)

    os.remove(temp_path)

    return JSONResponse(content={"status": "success"})


@app.post("/feedback")
async def feedback(feedback: Feedback):
    ls_client.create_feedback(
        feedback.run_id,
        key="user-score",
        score=feedback.score,
    )
    return JSONResponse(content={"status": "success"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
