import sqlite3
import hashlib

conn = sqlite3.connect('backend/ecommerce.db')
cursor = conn.cursor()

# Check if admin user exists
cursor.execute("SELECT * FROM users WHERE username='admin'")
user = cursor.fetchone()

hashed_pw = hashlib.sha256('admin123'.encode()).hexdigest()

if not user:
    cursor.execute("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)", ('admin', 'admin@example.com', hashed_pw, True))
    print("Created new admin user: admin / admin123")
else:
    cursor.execute("UPDATE users SET is_admin=1 WHERE username='admin'")
    cursor.execute("UPDATE users SET password=? WHERE username='admin'", (hashed_pw,))
    print("Updated existing 'admin' user to have admin privileges with password: admin123")

conn.commit()
conn.close()
