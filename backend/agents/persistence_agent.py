from state import InterviewState
from firebase_config import db
import datetime

def persistence_agent(state: InterviewState) -> dict:
    session_data = {
        "user_id": state["user_id"],
        "history": state["history"],
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }
    db.collection("interviews").add(session_data)
    return {"status": "done"}