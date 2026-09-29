from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatTurnResponse(BaseModel):
    reply: str = Field(description="Natural-language reply to show the employee, 2-5 sentences")
    leave_type: Optional[Literal["CL", "SL", "EL", "PL", "ML", "LWP"]] = Field(
        default=None, description="Leave type, only if the employee has specified or implied one this turn"
    )
    start_date: Optional[str] = Field(default=None, description="ISO date YYYY-MM-DD, only if mentioned this turn")
    end_date: Optional[str] = Field(default=None, description="ISO date YYYY-MM-DD, only if mentioned this turn")
    is_half_day: Optional[bool] = Field(default=None, description="Only set if explicitly discussed this turn")
    reason: Optional[str] = Field(default=None, description="Only set if the employee gave/updated a reason this turn")
    medical_certificate_confirmed: Optional[bool] = Field(
        default=None, description="Only set if the employee addressed the medical certificate this turn"
    )
    child_dob: Optional[str] = Field(default=None, description="ISO date, only if mentioned this turn")
    ready_to_submit: bool = Field(
        default=False,
        description="True only on the turn where the employee explicitly confirms submitting the current draft",
    )
