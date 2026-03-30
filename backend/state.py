from typing import TypedDict, Annotated
import operator

class InterviewState(TypedDict):
    user_id: str
    topic: str
    questions: list[str]
    answers: list[str]
    current_index: int
    scores: Annotated[list[float], operator.add]
    feedback_list: Annotated[list[str], operator.add]
    history: Annotated[list[dict], operator.add]
    is_coding: bool
    status: str  # "generating" | "evaluating" | "feedback" | "saving" | "done"