import os

import requests

import streamlit as st


def send_feedback(run_id: str, score: float):
    feedback_response = requests.post(
        f"http://fastapi:{os.getenv('PORT')}/feedback",
        json={"run_id": run_id, "score": score},
    )
    if feedback_response.status_code == 200:
        st.session_state.feedback_submitted = True
        st.success("Спасибо за отзыв!")
