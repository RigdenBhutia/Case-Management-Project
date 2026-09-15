# Case Management Backend

A simple REST API for managing IT support cases, built with FastAPI and PostgreSQL.

## Features
- Create, retrieve, and update support cases
- Input validation via Pydantic
- Structured logging (console + file)
- Automated tests with pytest

## Tech Stack
- Python 3.10
- FastAPI
- PostgreSQL + SQLAlchemy
- pytest

## Setup Instructions

1. Clone the repo:
```
git clone https://github.com/RigdenBhutia/Case-Management-Project.git
cd Case-Management-Project
```


2. Create and activate a virtual environment:
```
python -m venv venv
.\venv\Scripts\activate
```


3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set up PostgreSQL and create a database named `case_management_db`.

5. Create a `config/.env` file with:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/case_management_db
```

6. Run the server:
```
uvicorn src.main:app --reload
```

7. Visit `http://127.0.0.1:8000/docs` to test the API.

## Running Tests
```
python -m pytest
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /cases | Create a new case |
| GET | /cases/{id} | Retrieve a case by ID |
| PUT | /cases/{id} | Update a case |