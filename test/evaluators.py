from langchain import hub
from langchain_mistralai import ChatMistralAI
import os
import dotenv

dotenv.load_dotenv()

grade_prompt_answer_accuracy = hub.pull("langchain-ai/rag-answer-vs-reference")
grade_prompt_answer_helpfulness = hub.pull("langchain-ai/rag-answer-helpfulness")
grade_prompt_hallucinations = hub.pull("langchain-ai/rag-answer-hallucination")
grade_prompt_doc_relevance = hub.pull("langchain-ai/rag-document-relevance")


def answer_evaluator(run, example) -> dict:
    """
    A simple evaluator for RAG answer accuracy
    """

    # Get question, ground truth answer, RAG chain answer
    input_question = example.inputs["question"]
    reference = example.outputs["answer"]
    prediction = run.outputs["answer"]

    # LLM grader
    llm = ChatMistralAI(
        model="mistral-large-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0,
    )

    # Structured prompt
    answer_grader = grade_prompt_answer_accuracy | llm

    # Run evaluator
    score = answer_grader.invoke(
        {
            "question": input_question,
            "correct_answer": reference,
            "student_answer": prediction,
        }
    )
    score = score["Score"]

    return {"key": "answer_v_reference_score", "score": score}


def answer_helpfulness_evaluator(run, example) -> dict:
    """
    A simple evaluator for RAG answer helpfulness
    """

    # Get question, ground truth answer, RAG chain answer
    input_question = example.inputs["question"]
    prediction = run.outputs["answer"]

    # LLM grader
    llm = ChatMistralAI(
        model="mistral-large-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0,
    )

    # Structured prompt
    answer_grader = grade_prompt_answer_helpfulness | llm

    # Run evaluator
    score = answer_grader.invoke(
        {"question": input_question, "student_answer": prediction}
    )
    score = score["Score"]

    return {"key": "answer_helpfulness_score", "score": score}


def answer_hallucination_evaluator(run, example) -> dict:
    """
    A simple evaluator for generation hallucination
    """
    # RAG inputs
    contexts = run.outputs["contexts"]

    # RAG answer
    prediction = run.outputs["answer"]

    # LLM grader
    llm = ChatMistralAI(
        model="mistral-large-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0,
    )

    # Structured prompt
    answer_grader = grade_prompt_hallucinations | llm

    # Get score
    score = answer_grader.invoke({"documents": contexts, "student_answer": prediction})
    score = score["Score"]

    return {"key": "answer_hallucination", "score": score}


def docs_relevance_evaluator(run, example) -> dict:
    """
    A simple evaluator for document relevance
    """

    # RAG inputs
    input_question = example.inputs["question"]
    contexts = run.outputs["contexts"]

    # LLM grader
    llm = ChatMistralAI(
        model="mistral-large-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0,
    )

    # Structured prompt
    answer_grader = grade_prompt_doc_relevance | llm

    # Get score
    score = answer_grader.invoke({"question": input_question, "documents": contexts})
    score = score["Score"]

    return {"key": "document_relevance", "score": score}
