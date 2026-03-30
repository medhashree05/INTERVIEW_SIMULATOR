from state import InterviewState
from ml_scoring import score_answer

def evaluator_agent(state: InterviewState) -> dict:
    idx = state["current_index"]
    answer = state["answers"][idx]
    topic = state["topic"]
    keywords = [topic] + topic.split()
    score = score_answer(answer, keywords)

    return {
        "scores": [score],
        "status": "feedback",
    }