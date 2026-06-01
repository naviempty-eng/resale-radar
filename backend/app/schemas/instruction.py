from pydantic import BaseModel


class InstructionResponse(BaseModel):
    sent: bool
    content: str
