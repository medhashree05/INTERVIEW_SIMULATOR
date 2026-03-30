from langgraph.graph import StateGraph, END
from state import InterviewState
from agents.question_agent import question_agent
from agents.evaluator_agent import evaluator_agent
from agents.feedback_agent import feedback_agent
from agents.persistence_agent import persistence_agent

def should_continue(state: InterviewState) -> str:
    status = state["status"]
    if status == "evaluating":
        return "evaluator"
    if status == "feedback":
        return "feedback"
    if status == "saving":
        return "persistence"
    return END

def build_graph():
    builder = StateGraph(InterviewState)

    builder.add_node("question_gen", question_agent)
    builder.add_node("evaluator", evaluator_agent)
    builder.add_node("feedback", feedback_agent)
    builder.add_node("persistence", persistence_agent)

    builder.set_entry_point("question_gen")

    # After question gen, always go to evaluator
    builder.add_edge("question_gen", "evaluator")

    # After each agent, route based on status
    builder.add_conditional_edges("evaluator", should_continue)
    builder.add_conditional_edges("feedback", should_continue)
    builder.add_conditional_edges("persistence", should_continue)

    return builder.compile()

interview_graph = build_graph()