CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    group_name TEXT,
    student_id INTEGER REFERENCES students ON DELETE CASCADE
);

