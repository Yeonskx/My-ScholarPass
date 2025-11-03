import sqlite3
import os

# Ensure the folder exists
os.makedirs('database', exist_ok=True)

# Connect to the database
conn = sqlite3.connect('database/app.db')

# Read and execute the schema
with open('database/schema.sql') as f:
    conn.executescript(f.read())

conn.commit()
conn.close()

print("✅ Database created successfully at database/app.db")
