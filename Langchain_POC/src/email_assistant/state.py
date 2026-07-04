"""Shared graph state. Subclasses MessagesState so every node can read and
append to `messages`, plus our own email-specific fields."""
from typing import Literal, Optional

from langgraph.graph import MessagesState


class EmailState(MessagesState):
    # Raw incoming email
    email_from: str
    email_subject: str
    email_body: str

    # Triage output
    classification: Optional[Literal["respond", "notify", "ignore"]]

    # Work products built up as agents run
    calendar_checked: bool
    draft: Optional[str]