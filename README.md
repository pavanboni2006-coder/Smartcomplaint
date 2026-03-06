# Smart Complaint Management System

A **college mini-project** web application for submitting and managing public complaints built with **Python Flask**, **MySQL**, and **HTML/CSS/JavaScript**.

---

## 📁 Folder Structure

```
smart_complaint/
├── app.py                  # Main Flask application (backend)
├── create_admin.py         # Run once to create the admin account
├── database.sql            # MySQL schema and seed data
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── static/
│   ├── css/style.css       # Stylesheet
│   └── js/script.js        # JavaScript
├── templates/
│   ├── base.html           # Shared layout
│   ├── index.html          # Home / landing page
│   ├── register.html       # User registration
│   ├── login.html          # User login
│   ├── dashboard.html      # User dashboard
│   ├── submit_complaint.html
│   ├── my_complaints.html
│   ├── complaint_detail.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── admin_complaints.html
│   ├── admin_update.html
│   └── report.html
└── uploads/                # Auto-created; stores uploaded photos
```

---

## ⚙️ Prerequisites

- **Python 3.8+** — [Download](https://python.org)
- **MySQL 8.0+** — [Download](https://dev.mysql.com/downloads/)
- **pip** (comes with Python)

---

## 🚀 Step-by-Step Setup

### Step 1 — Clone / Download the Project

Place the `smart_complaint/` folder wherever you like.

---

### Step 2 — Set Up the MySQL Database

1. Open **MySQL Command Line Client** or **phpMyAdmin**
2. Run the SQL file to create the database and tables:

```sql
-- In MySQL CLI:
source /full/path/to/smart_complaint/database.sql;
```

Or copy-paste the contents of `database.sql` into phpMyAdmin's SQL tab.

**Tables created:**
| Table | Purpose |
|---|---|
| `users` | Registered users |
| `admins` | Admin accounts |
| `departments` | Department list |
| `complaints` | All submitted complaints |

---

### Step 3 — Install Python Dependencies

Open a terminal in the `smart_complaint/` folder and run:

```bash
pip install -r requirements.txt
```

This installs: `Flask`, `Flask-MySQLdb`, `Werkzeug`

---

### Step 4 — Configure MySQL Credentials

Open `app.py` and find this section (around line 20):

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'      # ← change to your MySQL username
app.config['MYSQL_PASSWORD'] = ''      # ← change to your MySQL password
app.config['MYSQL_DB'] = 'smart_complaint_db'
```

**Do the same in `create_admin.py`** (same four lines).

---

### Step 5 — Create the Admin Account

Run the admin setup script **once**:

```bash
python create_admin.py
```

Expected output:
```
✅ Admin account created successfully!
   Username: admin
   Password: admin123
```

> **Why this step?** Werkzeug's password hashing is dynamic; running the script ensures the hash stored in MySQL matches the password correctly.

---

### Step 6 — Run the Application

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Step 7 — Open the App

Open your browser and go to: **http://127.0.0.1:5000**

---

## 🔑 Default Credentials

| Role | Username/Email | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| User | Register yourself at `/register` | — |

> **Admin login page:** `http://127.0.0.1:5000/admin/login`

---

## 🌐 Application Routes

| URL | Description |
|---|---|
| `/` | Home / Landing page |
| `/register` | User registration |
| `/login` | User login |
| `/dashboard` | User dashboard |
| `/submit` | Submit a complaint |
| `/my_complaints` | View my complaints |
| `/complaint/<id>` | View complaint detail |
| `/admin/login` | Admin login |
| `/admin/dashboard` | Admin dashboard |
| `/admin/complaints` | All complaints (with search/filter) |
| `/admin/report` | Complaint report by category |

---

## 🧩 Features

### User Module
- ✅ Registration & login with password hashing (werkzeug)
- ✅ Submit complaint with Title, Description, Category, optional photo
- ✅ Unique complaint ID (e.g., `CMP-AB3X7`)
- ✅ View and track all submitted complaints
- ✅ Status tracking: **Pending → In Progress → Resolved**
- ✅ Filter complaints by status
- ✅ Live search on complaint list

### Admin Module
- ✅ Separate admin login
- ✅ Dashboard with total / pending / in-progress / resolved counts
- ✅ View all complaints with search + status filter
- ✅ Update complaint status
- ✅ Assign complaint to department
- ✅ Add admin notes / response
- ✅ Delete invalid complaints
- ✅ Report page: complaints by category and department with resolution rates

---

## 🗄️ MySQL Commands Reference

```sql
-- View all complaints
USE smart_complaint_db;
SELECT * FROM complaints;

-- View complaints by status
SELECT * FROM complaints WHERE status = 'Pending';

-- View all users
SELECT id, name, email, created_at FROM users;

-- Manually reset admin password (after getting hash from Python)
-- python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('newpassword'))"
UPDATE admins SET password_hash = '<paste_hash_here>' WHERE username = 'admin';

-- Drop and recreate the database (fresh start)
DROP DATABASE smart_complaint_db;
-- Then re-run database.sql
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: flask_mysqldb` | Run `pip install Flask-MySQLdb` |
| MySQL connection error | Check `MYSQL_USER` and `MYSQL_PASSWORD` in `app.py` |
| Admin login fails | Run `python create_admin.py` again |
| Image not showing | Check the `uploads/` folder exists and is writable |
| Port 5000 in use | Change `port=5000` in `app.py` to another port like `5001` |

---

## 📚 Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Backend language |
| Flask | 3.0.3 | Web framework |
| Flask-MySQLdb | 2.0.0 | MySQL connector |
| Werkzeug | 3.0.3 | Password hashing, file upload |
| MySQL | 8.0+ | Database |
| HTML/CSS/JS | — | Frontend |

---

## 👩‍💻 Suitable For

- ✅ College mini-project / semester project
- ✅ Beginner Python Flask learners
- ✅ Learning session management and form handling
- ✅ Learning MySQL with Flask

---

*Developed as a college mini-project — Smart Complaint Management System*
