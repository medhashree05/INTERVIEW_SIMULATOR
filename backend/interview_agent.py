from llm_engine import generate_question, generate_feedback
from ml_scoring import score_answer
from firebase_config import db
import datetime


# ── Question structure for 8 questions ──
# Each tuple: (difficulty, type)

QUESTION_PLAN = [
    ("easy",   "theory"),     # Q1
    ("easy",   "theory"),     # Q2
    ("easy",   "theory"),     # Q3
    ("medium", "coding"),     # Q4
    ("medium", "coding"),     # Q5
    ("medium", "coding"),     # Q6
    ("hard",   "scenario"),   # Q7
    ("hard",   "scenario"),   # Q8
]


# ── Step 1: Generate questions before user answers ──

def generate_questions(topic: str, count: int = 8, is_coding: bool = True) -> list[str]:
    """
    Generate `count` questions following a progressive difficulty + mixed type plan.
    Falls back gracefully if count != 8 by trimming or padding the plan.
    """
    questions = []

    # Use the plan up to `count`, cycling the last entry if count > plan length
    plan = QUESTION_PLAN[:count]
    while len(plan) < count:
        plan.append(QUESTION_PLAN[-1])

    for difficulty, q_type in plan:
        # Swap "coding" → "practical" for non-technical topics
        resolved_type = q_type if (q_type != "coding" or is_coding) else "practical"
        question = generate_question(topic, difficulty, resolved_type)
        questions.append(question)

    return questions


# ── Step 2: Evaluate answers against questions ──

def interview_agent(topic: str, questions: list[str], answers: list[str]) -> list[dict]:
    history = []

    for i, (question, answer) in enumerate(zip(questions, answers)):
        keywords = [topic] + topic.split()
        score = score_answer(answer, keywords)
        feedback = generate_feedback(answer, score)

        history.append({
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback
        })

    return history


# ── Firestore Helpers ──

def save_session(user_id: str, history: list[dict]):
    session_data = {
        "user_id": user_id,
        "history": history,
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    }
    db.collection("interviews").add(session_data)


def get_user_history(user_id: str) -> list[dict]:
    docs = db.collection("interviews").where("user_id", "==", user_id).stream()
    return [doc.to_dict() for doc in docs]


def summarize_performance(history: list[dict]) -> dict:
    if not history:
        return {"average_score": 0, "total_questions": 0}

    avg_score = sum(h["score"] for h in history) / len(history)
    return {
        "average_score": round(avg_score, 2),
        "total_questions": len(history)
    }


# ── Local Test ──

if __name__ == "__main__":
    topic = "data structures"

    print("Generating questions...")
    questions = generate_questions(topic, count=8, is_coding=True)
    for i, q in enumerate(questions):
        plan = QUESTION_PLAN[i]
        print(f"Q{i+1} [{plan[0].upper()} / {plan[1]}]: {q}")

    test_answers = [
        "Stack follows LIFO principle.",
        "Queue follows FIFO principle.",
        "A linked list allows dynamic memory allocation.",
        "def reverse(arr): return arr[::-1]",
        "Binary search runs in O(log n).",
        "def fib(n): return n if n<=1 else fib(n-1)+fib(n-2)",
        "I would use a hash map to detect cycles in the graph.",
        "In a real system I'd use a priority queue for scheduling.",
    ]

    print("\nEvaluating answers...")
    history = interview_agent(topic, questions, test_answers)

    for h in history:
        print(f"\nQ: {h['question']}")
        print(f"A: {h['answer']}")
        print(f"Score: {h['score']}")
        print(f"Feedback: {h['feedback']}")

    print("\nSummary:", summarize_performance(history))