import os
import time

import dotenv
import requests
from evaluators import (
    answer_evaluator,
    answer_hallucination_evaluator,
    answer_helpfulness_evaluator,
    docs_relevance_evaluator,
)
from langsmith import Client
from langsmith.evaluation import evaluate

dotenv.load_dotenv()


def predict_rag_answer(example: dict):
    """Use this for answer evaluation"""
    time.sleep(2)
    response = requests.post(
        "http://localhost:8080/rag_response",
        json={"message": example["question"]},
    )
    time.sleep(2)
    return {"answer": response.json()["response"]}


def predict_rag_answer_with_context(example: dict):
    """Use this for evaluation of retrieved documents and hallucinations"""
    time.sleep(2)
    response = requests.post(
        "http://localhost:8080/rag_response",
        json={"message": example["question"]},
    )
    time.sleep(2)
    return {
        "answer": response.json()["response"],
        "contexts": response.json()["context"],
    }


if __name__ == "__main__":
    dataset_name = os.getenv("DATASET_NAME")

    client = Client(api_key=os.getenv("LANGCHAIN_API_KEY"))

    experiment_results = evaluate(
        predict_rag_answer,
        data=dataset_name,
        evaluators=[answer_evaluator],
        experiment_prefix="rag-answer-v-reference",
        client=client,
    )

    experiment_results = evaluate(
        predict_rag_answer,
        data=dataset_name,
        evaluators=[answer_helpfulness_evaluator],
        experiment_prefix="rag-answer-helpfulness",
        client=client,
    )

    experiment_results = evaluate(
        predict_rag_answer_with_context,
        data=dataset_name,
        evaluators=[answer_hallucination_evaluator],
        experiment_prefix="rag-answer-hallucination",
        client=client,
    )

    experiment_results = evaluate(
        predict_rag_answer_with_context,
        data=dataset_name,
        evaluators=[docs_relevance_evaluator],
        experiment_prefix="rag-doc-relevance",
        client=client,
    )
