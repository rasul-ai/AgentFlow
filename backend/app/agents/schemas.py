from pydantic import BaseModel, Field


class EligibilityExplanation(BaseModel):
    summary: str = Field(description="2-4 sentence, professional, employee-facing explanation of the decision")
    cited_sections: list[str] = Field(description="Policy section letters referenced, e.g. ['D', 'F']")


class ApplicationDraft(BaseModel):
    application_text: str = Field(
        description="A formal leave application letter addressed to the employee's manager, ready to send"
    )
