from pydantic import BaseModel, Field


class WorkOrderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: str = Field(default="open", max_length=20)
    priority: str = Field(default="normal", max_length=20)


class WorkOrderUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: str = Field(max_length=20)
    priority: str = Field(max_length=20)
    is_complete: bool
    

class WorkOrderResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    is_complete: bool

    class Config:
        from_attributes = True