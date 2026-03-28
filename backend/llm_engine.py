from google import genai
import os
from itertools import cycle
from dotenv import load_dotenv

load_dotenv()

# ── Load all 4 API keys ──
_RAW_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
]

API_KEYS = [k for k in _RAW_KEYS if k]

if not API_KEYS:
    raise ValueError("No Gemini API keys found in .env!")

print(f"[llm_engine] Loaded {len(API_KEYS)} API key(s) — round-robin enabled")

# ── Round-robin key iterator ──
_key_cycle = cycle(API_KEYS)

def _get_next_client():
    """Return a fresh client configured with the next API key."""
    key = next(_key_cycle)
    return genai.Client(api_key=key)          # ✅ new style


# ── Question type instructions ──
TYPE_INSTRUCTION = {
    "theory":    "a conceptual/theoretical question that tests knowledge and understanding",
    "coding":    "a coding or problem-solving question where the candidate must write code or pseudocode",
    "practical": "a practical real-world application question (no coding required)",
    "scenario":  "a scenario-based question describing a real situation the candidate must reason through",
}


# ── Generate one question (uses next key in rotation) ──
def generate_question(topic: str = "machine learning", difficulty: str = "easy", q_type: str = "theory") -> str:
    try:
        client = _get_next_client()
        instruction = TYPE_INSTRUCTION.get(q_type, "a question")

        prompt = f"""
        Generate ONE interview question.

        Topic: {topic}
        Difficulty: {difficulty}
        Question Type: {instruction}

        Rules:
        - Return ONLY the question, nothing else
        - No numbering, no labels, no explanation
        - Make it specific to the topic and match the difficulty level
        """

        response = client.models.generate_content(   # ✅ new style
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        return response.text.strip()

    except Exception as e:
        return f"Error generating question: {e}"


# ── Generate feedback (uses next key in rotation) ──
def generate_feedback(answer: str, score: int) -> str:
    try:
        client = _get_next_client()

        prompt = f"""
        You are an interview evaluator.

        Candidate Answer:
        {answer}

        Score: {score}/10

        Give:
        - Strengths
        - Weaknesses
        - How to improve

        Keep it concise and structured.
        """

        response = client.models.generate_content(   # ✅ new style
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        return response.text

    except Exception as e:
        return f"Error generating feedback: {e}"


if __name__ == "__main__":
    for q_type in ["theory", "theory", "theory", "coding", "coding", "coding", "scenario", "scenario"]:
        q = generate_question("data structures", "medium", q_type)
        print(f"[{q_type.upper()}] {q}\n")