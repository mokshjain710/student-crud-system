# 🎓 Student Records Management System (DBMS CRUD Web Application)

A complete, college-ready DBMS Mini-Project demonstrating **CRUD (Create, Read, Update, Delete)** operations with a modern **HTML, CSS, and JavaScript** frontend, **Python Flask** REST API backend, and **MySQL** database.

---

## 📌 Project Overview
* **Title:** Student Records Management System
* **Tech Stack:**
  * **Frontend:** HTML5, CSS3 (Modern Responsive UI), JavaScript (ES6 `fetch` API)
  * **Backend:** Python (Flask REST API)
  * **Database:** MySQL (with automatic fallback to SQLite if MySQL is temporarily offline)
* **CRUD Capabilities:**
  * ➕ **Create (C):** Add new student records (`INSERT INTO students ...`)
  * 👁️ **Read (R):** View student list with live search, department filters, and stats (`SELECT ... FROM students`)
  * ✏️ **Update (U):** Edit student details, semester, and CGPA via interactive modal (`UPDATE students SET ...`)
  * 🗑️ **Delete (D):** Remove student records with confirmation dialogue (`DELETE FROM students WHERE id = ...`)

---

## 🚀 Quick Start Guide (Windows)

### Option 1: 1-Click Launch (Easiest)
1. Simply double-click the **`run.bat`** file.
2. It will automatically install the required dependencies (`Flask`, `PyMySQL`, `cryptography`), launch the server, and open `http://127.0.0.1:5000` in your browser!

### Option 2: Manual Terminal / Command Prompt
1. Open Command Prompt inside this project folder:
   ```cmd
   cd student_crud_project
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Start the application:
   ```cmd
   python app.py
   ```
4. Open your browser and visit:
   ```
   http://127.0.0.1:5000
   ```

---

## ⚙️ MySQL Database Configuration

Open **`config.json`** to configure your MySQL connection:

```json
{
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "student_crud_db"
  },
  "use_sqlite_fallback_if_mysql_unavailable": true
}
```

> **Note on Zero-Configuration:**
> The app automatically runs `CREATE DATABASE IF NOT EXISTS student_crud_db` and creates the `students` table along with sample records on first startup!
> If your MySQL server is turned off or you haven't set up the password yet, the app gracefully runs with the built-in SQLite database so your demonstration never fails.

---

## 🗄️ SQL Schema Reference (`database.sql`)

If your professor or lab evaluator asks you to execute the SQL queries manually in **MySQL Workbench** or the **MySQL Command Line**, you can run `database.sql`:

```sql
CREATE DATABASE IF NOT EXISTS student_crud_db;
USE student_crud_db;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    cgpa DECIMAL(3, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📚 Viva Questions & Answers for DBMS Lab

1. **What does CRUD stand for?**
   * **C**reate (`INSERT`)
   * **R**ead (`SELECT`)
   * **U**pdate (`UPDATE`)
   * **D**elete (`DELETE`)

2. **Why do we need a backend server (Flask) between JavaScript and MySQL?**
   * Web browsers cannot directly connect to MySQL for security and protocol reasons. JavaScript runs in the client's browser, whereas the backend runs securely on the server with database connection privileges.

3. **What is a Primary Key and how is it used here?**
   * `id` is the Primary Key with `AUTO_INCREMENT`. It uniquely identifies each record in the `students` table.

4. **What is the `UNIQUE` constraint on `roll_no`?**
   * It ensures that no two students can have the exact same Roll Number in the database, preserving data integrity.
