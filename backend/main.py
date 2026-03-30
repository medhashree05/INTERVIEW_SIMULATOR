from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from graph import interview_graph
from agents.question_agent import question_agent
from llm_engine import generate_question
from agents.question_agent import is_coding_topic  
from firebase_config import db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class QuestionRequest(BaseModel):
    topic: str
    count: Optional[int] = 8
    difficulty: Optional[str] = "progressive"
    types: Optional[list[str]] = ["theory", "coding", "scenario"]

class InterviewRequest(BaseModel):
    user_id: str
    topic: str
    questions: list[str]
    answers: list[str]

@app.get("/")
def home():
    return {"message": "Interview AI — LangGraph multi-agent running"}

@app.post("/get_questions")
def get_questions(data: QuestionRequest):
    # Question gen is stateless, call agent directly
    is_coding = is_coding_topic(data.topic)
    result = question_agent({
        "topic": data.topic,
        "is_coding": is_coding,
        "user_id": "", "answers": [], "scores": [],
        "feedback_list": [], "history": [], "current_index": 0,
        "questions": [], "status": "generating",
    })
    return {"questions": result["questions"], "is_coding_topic": is_coding}

@app.post("/start_interview")
def start_interview(data: InterviewRequest):
    initial_state: dict = {
        "user_id": data.user_id,
        "topic": data.topic,
        "questions": data.questions,
        "answers": data.answers,
        "current_index": 0,
        "scores": [],
        "feedback_list": [],
        "history": [],
        "is_coding": is_coding_topic(data.topic),
        "status": "evaluating",  # skip question gen, answers already provided
    }
    final_state = interview_graph.invoke(initial_state)
    return {"history": final_state["history"]}

@app.get("/history/{user_id}")
def get_history(user_id: str):
    docs = db.collection("interviews").where("user_id", "==", user_id).stream()
    return {"history": [doc.to_dict() for doc in docs]}