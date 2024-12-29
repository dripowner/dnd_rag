from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Feedback(BaseModel):
    run_id: str
    score: float
