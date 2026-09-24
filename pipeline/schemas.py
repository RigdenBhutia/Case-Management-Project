from pydantic import BaseModel, ValidationError

class CaseSchema(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: str
    category_id: int
    customer_id: int

def validate_row(row: dict):
    try:
        CaseSchema(**row)
        return True, None
    except ValidationError as e:
        return False, str(e)