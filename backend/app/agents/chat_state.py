from typing import TypedDict


class ChatAgentState(TypedDict, total=False):
    # Inputs
    employee_context: str
    balance_context: str
    holiday_context: str
    history: list[dict]
    user_message: str
    collected_slots: dict

    # Populated by graph nodes
    retrieved_chunks: list[dict]
    reply: str
    updated_slots: dict
    missing_fields: list[str]
    ready_to_submit: bool
