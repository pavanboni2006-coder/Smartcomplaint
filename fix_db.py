import sqlite3
from app import init_db

db = sqlite3.connect("complaint.db")
db.execute("DROP TABLE IF EXISTS admins")
db.commit()
db.close()

init_db()
print("Fixed admins table and seeded default admin.")
