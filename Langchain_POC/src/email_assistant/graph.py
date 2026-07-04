"""Multi-agent email assistant — Phase 1 skeleton.

Flow:  triage → (respond) → supervisor → response/calendar agents
       → human approval → send.  All nodes live here for now; we split
       them into nodes/ in Phase 2.

Run locally:  langgraph dev   (then open LangGraph Studio)
"""
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field

from email_assistant.models import get_model
from email_assistant.state import EmailState


# --- structured outputs -----------------------------------------------------

class TriageDecision(BaseModel):
    classification: Literal["respond", "notify", "ignore"] = Field(
        description="respond = needs a reply; notify = FYI only; ignore = spam/no action"
    )
    reasoning: str = Field(description="one short sentence")


class SupervisorDecision(BaseModel):
    next_agent: Literal["response_agent", "calendar_agent", "finish"] = Field(
        description="Which specialist runs next, or finish once a draft is ready."
    )


def _email_text(state: EmailState) -> str:
    return (
        f"From: {state['email_from']}\n"
        f"Subject: {state['email_subject']}\n\n"
        f"{state['email_body']}"
    )


# --- nodes ------------------------------------------------------------------

def triage(state: EmailState) -> dict:
    model = get_model("triage").with_structured_output(TriageDecision)
    decision = model.invoke([
        HumanMessage(
            "You triage incoming email. Classify the message below.\n\n"
            + _email_text(state)
        )
    ])
    return {"classification": decision.classification}


def route_after_triage(state: EmailState) -> Literal["supervisor", "notify", "__end__"]:
    if state["classification"] == "respond":
        return "supervisor"
    if state["classification"] == "notify":
        return "notify"
    return END


def notify(state: EmailState) -> dict:
    # Phase 1: just record it. Later this pings you (Slack/Teams) without replying.
    return {"messages": [AIMessage(f"FYI only — no reply needed: {state['email_subject']}")]}


def supervisor(state: EmailState) -> Command[Literal["response_agent", "calendar_agent", "human_approval"]]:
    model = get_model("supervisor").with_structured_output(SupervisorDecision)
    context = (
        f"Draft ready: {bool(state.get('draft'))}. "
        f"Calendar checked: {state.get('calendar_checked', False)}. "
        "Route to calendar_agent if the email asks to schedule/meet and the calendar "
        "isn't checked yet. Route to response_agent to draft a reply. "
        "Choose finish once a draft exists."
    )
    decision = model.invoke([HumanMessage(context + "\n\n" + _email_text(state))])
    if decision.next_agent == "finish":
        return Command(goto="human_approval")
    return Command(goto=decision.next_agent)


def response_agent(state: EmailState) -> Command[Literal["supervisor"]]:
    model = get_model("response")
    reply = model.invoke([
        HumanMessage(
            "Draft a concise, professional reply to this email. "
            "Return only the reply body.\n\n" + _email_text(state)
        )
    ])
    return Command(goto="supervisor", update={"draft": reply.content})


def calendar_agent(state: EmailState) -> Command[Literal["supervisor"]]:
    # Phase 1: mock availability. Real calendar tool comes in Phase 2.
    slots = "Tue 3pm, Wed 11am, Thu 4pm"
    return Command(
        goto="supervisor",
        update={
            "calendar_checked": True,
            "messages": [AIMessage(f"Mock availability: {slots}")],
        },
    )


def human_approval(state: EmailState) -> Command[Literal["send", "__end__"]]:
    decision = interrupt({
        "draft": state.get("draft", ""),
        "instructions": "Resume with {'action': 'approve' | 'edit' | 'reject', 'draft': '<text if editing>'}",
    })
    action = decision.get("action")
    if action == "approve":
        return Command(goto="send")
    if action == "edit":
        return Command(goto="send", update={"draft": decision.get("draft", state.get("draft"))})
    return END  # reject


def send(state: EmailState) -> dict:
    # Phase 1: mock send. Real Gmail/Graph tool comes in Phase 5.
    return {"messages": [AIMessage(f"SENT:\n{state.get('draft', '')}")]}


# --- assemble ---------------------------------------------------------------

builder = StateGraph(EmailState)
builder.add_node("triage", triage)
builder.add_node("notify", notify)
builder.add_node("supervisor", supervisor)
builder.add_node("response_agent", response_agent)
builder.add_node("calendar_agent", calendar_agent)
builder.add_node("human_approval", human_approval)
builder.add_node("send", send)

builder.add_edge(START, "triage")
builder.add_conditional_edges("triage", route_after_triage)
builder.add_edge("notify", END)
builder.add_edge("send", END)

# `langgraph dev` provides persistence, so we compile WITHOUT a checkpointer here.
# For a standalone script with interrupts, compile with InMemorySaver instead.
graph = builder.compile()