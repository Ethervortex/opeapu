CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE activity (
    course_id INTEGER REFERENCES courses(id),
    student_id INTEGER REFERENCES students(id),
    PRIMARY KEY (course_id, student_id),
    activity_score INTEGER,
    activity_date TEXT
);

CREATE TABLE course_students (
    course_id INTEGER REFERENCES courses(id),
    student_id INTEGER REFERENCES students(id),
    PRIMARY KEY (course_id, student_id),
    grade INTEGER
);