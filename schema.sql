-- Case Management System - Database Schema

CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_cases_id ON cases (id);