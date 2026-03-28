from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from interview_agent import interview_agent, generate_questions
from firebase_config import db
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ──

class QuestionRequest(BaseModel):
    topic: str
    count: Optional[int] = 8                          # ← accept count from frontend
    difficulty: Optional[str] = "progressive"         # ← accept difficulty
    types: Optional[list[str]] = ["theory", "coding", "scenario"]  # ← accept types


class InterviewRequest(BaseModel):
    user_id: str
    topic: str
    questions: list[str]
    answers: list[str]


# ── Helper: detect if topic is coding/technical ──

CODING_TOPICS = {
    "dsa", "data structures", "algorithms", "python", "java", "c++", "javascript",
    "react", "node", "nodejs", "ml", "machine learning", "deep learning", "ai",
    "artificial intelligence", "sql", "databases", "os", "operating systems",
    "networking", "system design", "django", "flask", "fastapi", "typescript",
    "css", "html", "devops", "docker", "kubernetes", "git", "aws", "cloud",
}

def is_coding_topic(topic: str) -> bool:
    return any(keyword in topic.lower() for keyword in CODING_TOPICS)


# ── Routes ──

@app.get("/")
def home():
    return {"message": "Interview AI running"}


@app.post("/get_questions")
def get_questions(data: QuestionRequest):
    is_coding = is_coding_topic(data.topic)

    questions = generate_questions(
        topic=data.topic,
        count=data.count,
        is_coding=is_coding,
    )

    return {
        "questions": questions,
        "is_coding_topic": is_coding,   # ← frontend uses this to show Coding vs Practical
    }


@app.post("/start_interview")
def start_interview(data: InterviewRequest):
    history = interview_agent(data.topic, data.questions, data.answers)

    session_data = {
        "user_id": data.user_id,
        "history": history,
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    }

    db.collection("interviews").add(session_data)

    return {"history": history}


@app.get("/history/{user_id}")
def get_history(user_id: str):
    docs = db.collection("interviews").where("user_id", "==", user_id).stream()
    results = [doc.to_dict() for doc in docs]
    return {"history": results}