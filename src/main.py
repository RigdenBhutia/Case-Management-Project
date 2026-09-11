from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database import SessionLocal
from src.models import Case
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),           # still prints to terminal
        logging.FileHandler("app.log")     # also saves to a file
    ]
)
logger = logging.getLogger(__name__)

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
    logger.info(f"Case created: id={new_case.id}, title={new_case.title}")
    return new_case

from fastapi import HTTPException

@app.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        logger.warning(f"Case not found: id={case_id}")
        raise HTTPException(status_code=404, detail="Case not found")
    logger.info(f"Case retrieved: id={case_id}")
    return case


from typing import Optional

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

@app.put("/cases/{case_id}")
def update_case(case_id: int, case_update: CaseUpdate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        logger.warning(f"Case not found for update: id={case_id}")
        raise HTTPException(status_code=404, detail="Case not found")

    if case_update.title is not None:
        case.title = case_update.title
    if case_update.description is not None:
        case.description = case_update.description
    if case_update.status is not None:
        case.status = case_update.status

    db.commit()
    db.refresh(case)
    logger.info(f"Case updated: id={case_id}")
    return case