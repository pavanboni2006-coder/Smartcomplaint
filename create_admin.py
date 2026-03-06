# ============================================================
# create_admin.py - Reset or re-create the admin account
# Usage: python create_admin.py
# ============================================================

import sqlite3
import os
from werkzeug.security import generate_password_hash

# Path to the SQLite database (same as in app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'complaint.db')

if not os.path.exists(DATABASE):
    print("❌ Database not found. Please run 'python app.py' first to initialize it.")
    exit(1)

conn = sqlite3.connect(DATABASE)
hashed = generate_password_hash('admin123')

# Delete existing admin and re-insert
conn.execute("DELETE FROM admins WHERE username = 'admin'")
conn.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ('admin', hashed))
conn.commit()
conn.close()

print("✅ Admin account created/reset successfully!")
print("   Username : admin")
print("   Password : admin123")
