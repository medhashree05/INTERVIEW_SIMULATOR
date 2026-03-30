from state import InterviewState
from llm_engine import generate_feedback

def feedback_agent(state: InterviewState) -> dict:
    idx = state["current_index"]
    score = state["scores"][idx]
    answer = state["answers"][idx]
    feedback = generate_feedback(answer, score)

    entry = {
        "question": state["questions"][idx],
        "answer": answer,
        "score": score,
        "feedback": feedback,
    }

    next_index = idx + 1
    answers_done = next_index >= len(state["answers"])

    return {
        "feedback_list": [feedback],
        "history": [entry],
        "current_index": next_index,
        "status": "saving" if answers_done else "evaluating",
    }