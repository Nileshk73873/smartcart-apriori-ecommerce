import os
import sqlite3
from pathlib import Path
import bcrypt

db_path = Path(__file__).resolve().parent / "backend" / "ecommerce.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if admin user exists
cursor.execute("SELECT * FROM users WHERE username='admin'")
user = cursor.fetchone()

admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
hashed_pw = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

if not user:
    cursor.execute(
        "INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
        ("admin", "admin@example.com", hashed_pw, True),
    )
    print("Created new admin user: admin")
else:
    cursor.execute("UPDATE users SET is_admin=1 WHERE username='admin'")
    cursor.execute("UPDATE users SET password=? WHERE username='admin'", (hashed_pw,))
    print("Updated existing 'admin' user to have admin privileges.")

conn.commit()
conn.close()

