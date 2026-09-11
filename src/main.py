from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database import SessionLocal
from src.models import Case

app = FastAPI()

class CaseCreate(BaseModel):
    title: str
    description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/cases")
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    new_case = Case(title=case.title, description=case.description)
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

from fastapi import HTTPException

@app.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case