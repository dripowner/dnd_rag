import os

import requests
from dotenv import load_dotenv
from utils import send_feedback

import streamlit as st

load_dotenv(".env")

st.title("Ассистент по правилам и игре в DnD")

with st.container():
    user_input = st.text_input("Ваш вопрос:", key="user_message")
    if st.button("Отправить"):
        if user_input:
            response = requests.post(
                f"http://fastapi:{os.getenv('PORT')}/rag_response",
                json={"message": user_input},
            )
            st.write(response.json()["response"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "👍 Полезно",
                    key="like",
                    on_click=send_feedback,
                    args=(response.json()["run_id"], 1.0),
                ):
                    pass

            with col2:
                if st.button(
                    "👎 Не полезно",
                    key="dislike",
                    on_click=send_feedback,
                    args=(response.json()["run_id"], 0.0),
                ):
                    pass
        else:
            st.warning("Пожалуйста, введите сообщение")

with st.container():
    uploaded_file = st.file_uploader(
        "Загрузить PDF или TXT файл с правилами", type=["pdf", "txt"]
    )
    if uploaded_file is not None:
        if st.button("Отправить файл"):
            files = {"file": (uploaded_file)}
            response = requests.post(
                f"http://fastapi:{os.getenv('PORT')}/add_document", files=files
            )

            if response.status_code == 200:
                st.success("Файл успешно загружен!")
            else:
                st.error(f"Ошибка при загрузке файла: {response.json()}")
