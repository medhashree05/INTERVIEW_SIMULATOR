from state import InterviewState
from llm_engine import generate_question

CODING_TOPICS = {
    "dsa", "data structures", "algorithms", "python", "java", "c++", "javascript",
    "react", "node", "nodejs", "ml", "machine learning", "deep learning", "ai",
    "artificial intelligence", "sql", "databases", "os", "operating systems",
    "networking", "system design", "django", "flask", "fastapi", "typescript",
    "css", "html", "devops", "docker", "kubernetes", "git", "aws", "cloud",
}

def is_coding_topic(topic: str) -> bool:
    return any(keyword in topic.lower() for keyword in CODING_TOPICS)

QUESTION_PLAN = [
    ("easy", "theory"), ("easy", "theory"), ("easy", "theory"),
    ("medium", "coding"), ("medium", "coding"), ("medium", "coding"),
    ("hard", "scenario"), ("hard", "scenario"),
]

def question_agent(state: InterviewState) -> dict:
    topic = state["topic"]
    is_coding = is_coding_topic(topic)
    questions = []

    for difficulty, q_type in QUESTION_PLAN:
        resolved_type = q_type if (q_type != "coding" or is_coding) else "practical"
        questions.append(generate_question(topic, difficulty, resolved_type))

    return {
        "questions": questions,
        "is_coding": is_coding,
        "current_index": 0,
        "status": "evaluating",
    }