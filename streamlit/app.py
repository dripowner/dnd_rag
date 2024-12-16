import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv(".env")

st.title("DNDRag")

user_input = st.text_input("Ваш вопрос:", key="user_message")
if st.button("Отправить"):
    if user_input:
        response = requests.post(
            f"http://{os.getenv('HOST')}:{os.getenv('PORT')}/rag_response",
            json={"message": user_input},
        )
        st.write(response.json())
    else:
        st.warning("Пожалуйста, введите сообщение")
