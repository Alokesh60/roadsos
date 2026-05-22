from pydantic import BaseModel


class ContactCreate(BaseModel):

    user_id: str

    name: str

    phone: str

    relationship: str