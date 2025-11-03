-- Create the users table (sign-up/sign-in)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'provider')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
