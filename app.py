import os
import json
import sqlite3
import tempfile
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

app = Flask(__name__, static_folder=None)

# Load configuration
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
config = {
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "student_crud_db"
    },
    "use_sqlite_fallback_if_mysql_unavailable": True
}

if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r") as f:
            config.update(json.load(f))
    except Exception as e:
        print(f"[Warning] Could not load config.json: {e}")

# Environment variables override (for Vercel deployment)
if os.environ.get("MYSQL_HOST"):
    config["mysql"]["host"] = os.environ.get("MYSQL_HOST")
if os.environ.get("MYSQL_PORT"):
    try:
        config["mysql"]["port"] = int(os.environ.get("MYSQL_PORT"))
    except ValueError:
        pass
if os.environ.get("MYSQL_USER"):
    config["mysql"]["user"] = os.environ.get("MYSQL_USER")
if os.environ.get("MYSQL_PASSWORD") is not None:
    config["mysql"]["password"] = os.environ.get("MYSQL_PASSWORD")
if os.environ.get("MYSQL_DATABASE"):
    config["mysql"]["database"] = os.environ.get("MYSQL_DATABASE")

DB_MODE = "MYSQL"

# On Vercel / serverless, only /tmp is writable for SQLite
if os.environ.get("VERCEL"):
    SQLITE_DB_PATH = os.path.join(tempfile.gettempdir(), "student_crud.db")
else:
    SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "student_crud.db")

# Helper: Test & Initialize Database
def get_db_connection():
    global DB_MODE
    mysql_cfg = config.get("mysql", {})
    
    if DB_MODE == "MYSQL":
        try:
            import pymysql
            # Connect to MySQL server
            conn = pymysql.connect(
                host=mysql_cfg.get("host", "localhost"),
                port=mysql_cfg.get("port", 3306),
                user=mysql_cfg.get("user", "root"),
                password=mysql_cfg.get("password", ""),
                database=mysql_cfg.get("database", "student_crud_db"),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return conn, "MYSQL"
        except Exception as err:
            if config.get("use_sqlite_fallback_if_mysql_unavailable", True):
                print(f"[Notice] MySQL connection failed ({err}).")
                print("[Notice] Falling back to SQLite so your app continues to run seamlessly!")
                DB_MODE = "SQLITE"
            else:
                raise err

    # SQLite Fallback
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn, "SQLITE"


def init_database():
    global DB_MODE
    mysql_cfg = config.get("mysql", {})

    # 1. Try MySQL initialization first
    try:
        import pymysql
        # Connect to MySQL server without database first to ensure DB exists
        server_conn = pymysql.connect(
            host=mysql_cfg.get("host", "localhost"),
            port=mysql_cfg.get("port", 3306),
            user=mysql_cfg.get("user", "root"),
            password=mysql_cfg.get("password", ""),
            autocommit=True
        )
        with server_conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{mysql_cfg.get('database', 'student_crud_db')}`;")
        server_conn.close()

        # Connect with database and create table
        conn, mode = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    roll_no VARCHAR(20) NOT NULL UNIQUE,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    semester INT NOT NULL,
                    cgpa DECIMAL(4, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Ensure cgpa column supports up to 10.00
            cur.execute("ALTER TABLE students MODIFY COLUMN cgpa DECIMAL(4, 2) NOT NULL;")
            # Check if empty, insert demo records
            cur.execute("SELECT COUNT(*) AS cnt FROM students;")
            res = cur.fetchone()
            if res and res["cnt"] == 0:
                cur.execute("""
                    INSERT INTO students (roll_no, name, email, department, semester, cgpa) VALUES
                    ('CS101', 'Aarav Sharma', 'aarav.sharma@example.com', 'Computer Science', 6, 8.85),
                    ('CS102', 'Priya Patel', 'priya.patel@example.com', 'Computer Science', 6, 9.20),
                    ('IT201', 'Rohan Verma', 'rohan.verma@example.com', 'Information Technology', 4, 7.90),
                    ('EC301', 'Ananya Iyer', 'ananya.iyer@example.com', 'Electronics', 8, 8.40),
                    ('ME401', 'Vikram Singh', 'vikram.singh@example.com', 'Mechanical', 2, 7.50);
                """)
        conn.close()
        DB_MODE = "MYSQL"
        print("[Success] Connected to MySQL database and initialized 'students' table.")
        return
    except Exception as e:
        print(f"[Info] MySQL Init failed ({e}). Checking fallback configuration...")
        if config.get("use_sqlite_fallback_if_mysql_unavailable", True):
            DB_MODE = "SQLITE"
        else:
            print("[Error] Could not connect to MySQL and fallback is disabled.")
            return

    # 2. SQLite setup if MySQL was unavailable
    if DB_MODE == "SQLITE":
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                department TEXT NOT NULL,
                semester INTEGER NOT NULL,
                cgpa REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("SELECT COUNT(*) FROM students;")
        if cur.fetchone()[0] == 0:
            cur.executemany("""
                INSERT INTO students (roll_no, name, email, department, semester, cgpa)
                VALUES (?, ?, ?, ?, ?, ?);
            """, [
                ('CS101', 'Aarav Sharma', 'aarav.sharma@example.com', 'Computer Science', 6, 8.85),
                ('CS102', 'Priya Patel', 'priya.patel@example.com', 'Computer Science', 6, 9.20),
                ('IT201', 'Rohan Verma', 'rohan.verma@example.com', 'Information Technology', 4, 7.90),
                ('EC301', 'Ananya Iyer', 'ananya.iyer@example.com', 'Electronics', 8, 8.40),
                ('ME401', 'Vikram Singh', 'vikram.singh@example.com', 'Mechanical', 2, 7.50)
            ])
            conn.commit()
        conn.close()
        print("[Success] Initialized local SQLite fallback database 'student_crud.db'.")


# Auto-initialize database on first request (essential for Vercel serverless)
_db_initialized = False

@app.before_request
def ensure_db_init():
    global _db_initialized
    if not _db_initialized:
        init_database()
        _db_initialized = True

# =======================================================
# REST API ENDPOINTS (CRUD OPERATIONS)
# =======================================================

# [READ] Get All Students (supports search & filter)
@app.route("/api/students", methods=["GET"])
def get_students():
    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()

    conn, mode = get_db_connection()
    try:
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        if search:
            if mode == "MYSQL":
                query += " AND (name LIKE %s OR roll_no LIKE %s OR email LIKE %s)"
                term = f"%{search}%"
                params.extend([term, term, term])
            else:
                query += " AND (name LIKE ? OR roll_no LIKE ? OR email LIKE ?)"
                term = f"%{search}%"
                params.extend([term, term, term])

        if department:
            if mode == "MYSQL":
                query += " AND department = %s"
                params.append(department)
            else:
                query += " AND department = ?"
                params.append(department)

        query += " ORDER BY id DESC"

        if mode == "MYSQL":
            with conn.cursor() as cur:
                cur.execute(query, params)
                records = cur.fetchall()
        else:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            records = [dict(row) for row in rows]

        # Convert decimal or date objects for JSON safety
        for r in records:
            if "cgpa" in r and r["cgpa"] is not None:
                r["cgpa"] = float(r["cgpa"])
            if "created_at" in r and r["created_at"] is not None:
                r["created_at"] = str(r["created_at"])

        return jsonify({"status": "success", "data": records, "engine": mode})
    finally:
        conn.close()


# [READ] Get Single Student
@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    conn, mode = get_db_connection()
    try:
        if mode == "MYSQL":
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                record = cur.fetchone()
        else:
            cur = conn.cursor()
            cur.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            row = cur.fetchone()
            record = dict(row) if row else None

        if not record:
            return jsonify({"status": "error", "message": "Student not found"}), 404

        if "cgpa" in record and record["cgpa"] is not None:
            record["cgpa"] = float(record["cgpa"])
        if "created_at" in record and record["created_at"] is not None:
            record["created_at"] = str(record["created_at"])

        return jsonify({"status": "success", "data": record})
    finally:
        conn.close()


# [CREATE] Add New Student
@app.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json() or {}
    roll_no = data.get("roll_no", "").strip().upper()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    department = data.get("department", "").strip()
    semester = data.get("semester")
    cgpa = data.get("cgpa")

    # Validation
    if not all([roll_no, name, email, department, semester is not None, cgpa is not None]):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    try:
        semester = int(semester)
        cgpa = float(cgpa)
        if not (1 <= semester <= 8):
            return jsonify({"status": "error", "message": "Semester must be between 1 and 8."}), 400
        if not (0.0 <= cgpa <= 10.0):
            return jsonify({"status": "error", "message": "CGPA must be between 0.0 and 10.0."}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Semester and CGPA must be numeric."}), 400

    try:
        conn, mode = get_db_connection()
        try:
            if mode == "MYSQL":
                with conn.cursor() as cur:
                    # Check uniqueness of roll_no
                    cur.execute("SELECT id FROM students WHERE roll_no = %s", (roll_no,))
                    if cur.fetchone():
                        return jsonify({"status": "error", "message": f"Roll No '{roll_no}' already exists."}), 409

                    sql = """
                        INSERT INTO students (roll_no, name, email, department, semester, cgpa)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(sql, (roll_no, name, email, department, semester, cgpa))
                    new_id = cur.lastrowid
            else:
                cur = conn.cursor()
                cur.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
                if cur.fetchone():
                    return jsonify({"status": "error", "message": f"Roll No '{roll_no}' already exists."}), 409

                sql = """
                    INSERT INTO students (roll_no, name, email, department, semester, cgpa)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                cur.execute(sql, (roll_no, name, email, department, semester, cgpa))
                conn.commit()
                new_id = cur.lastrowid

            return jsonify({
                "status": "success",
                "message": "Student record created successfully!",
                "id": new_id
            }), 201
        finally:
            conn.close()
    except Exception as db_err:
        return jsonify({"status": "error", "message": str(db_err)}), 400


# [UPDATE] Update Student Record
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json() or {}
    roll_no = data.get("roll_no", "").strip().upper()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    department = data.get("department", "").strip()
    semester = data.get("semester")
    cgpa = data.get("cgpa")

    # Validation
    if not all([roll_no, name, email, department, semester is not None, cgpa is not None]):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    try:
        semester = int(semester)
        cgpa = float(cgpa)
        if not (1 <= semester <= 8):
            return jsonify({"status": "error", "message": "Semester must be between 1 and 8."}), 400
        if not (0.0 <= cgpa <= 10.0):
            return jsonify({"status": "error", "message": "CGPA must be between 0.0 and 10.0."}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Semester and CGPA must be numeric."}), 400

    try:
        conn, mode = get_db_connection()
        try:
            if mode == "MYSQL":
                with conn.cursor() as cur:
                    # Check if roll_no belongs to someone else
                    cur.execute("SELECT id FROM students WHERE roll_no = %s AND id != %s", (roll_no, student_id))
                    if cur.fetchone():
                        return jsonify({"status": "error", "message": f"Roll No '{roll_no}' is already used by another student."}), 409

                    sql = """
                        UPDATE students
                        SET roll_no = %s, name = %s, email = %s, department = %s, semester = %s, cgpa = %s
                        WHERE id = %s
                    """
                    affected = cur.execute(sql, (roll_no, name, email, department, semester, cgpa, student_id))
                    if affected == 0:
                        # Check if student exists
                        cur.execute("SELECT id FROM students WHERE id = %s", (student_id,))
                        if not cur.fetchone():
                            return jsonify({"status": "error", "message": "Student record not found."}), 404
            else:
                cur = conn.cursor()
                cur.execute("SELECT id FROM students WHERE roll_no = ? AND id != ?", (roll_no, student_id))
                if cur.fetchone():
                    return jsonify({"status": "error", "message": f"Roll No '{roll_no}' is already used by another student."}), 409

                sql = """
                    UPDATE students
                    SET roll_no = ?, name = ?, email = ?, department = ?, semester = ?, cgpa = ?
                    WHERE id = ?
                """
                cur.execute(sql, (roll_no, name, email, department, semester, cgpa, student_id))
                conn.commit()
                if cur.rowcount == 0:
                    cur.execute("SELECT id FROM students WHERE id = ?", (student_id,))
                    if not cur.fetchone():
                        return jsonify({"status": "error", "message": "Student record not found."}), 404

            return jsonify({"status": "success", "message": "Student record updated successfully!"})
        finally:
            conn.close()
    except Exception as db_err:
        return jsonify({"status": "error", "message": str(db_err)}), 400


# [DELETE] Delete Student Record
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn, mode = get_db_connection()
    try:
        if mode == "MYSQL":
            with conn.cursor() as cur:
                affected = cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
                if affected == 0:
                    return jsonify({"status": "error", "message": "Student not found."}), 404
        else:
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({"status": "error", "message": "Student not found."}), 404

        return jsonify({"status": "success", "message": "Student record deleted successfully!"})
    finally:
        conn.close()


# [STATS] Dashboard Summary Metrics
@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn, mode = get_db_connection()
    try:
        if mode == "MYSQL":
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS total, AVG(cgpa) AS avg_cgpa FROM students")
                stat = cur.fetchone() or {"total": 0, "avg_cgpa": 0}
                cur.execute("SELECT department, COUNT(*) AS count FROM students GROUP BY department ORDER BY count DESC")
                dept_counts = cur.fetchall()
        else:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS total, AVG(cgpa) AS avg_cgpa FROM students")
            row = cur.fetchone()
            stat = {"total": row["total"] or 0, "avg_cgpa": row["avg_cgpa"] or 0}
            cur.execute("SELECT department, COUNT(*) AS count FROM students GROUP BY department ORDER BY count DESC")
            dept_counts = [dict(r) for r in cur.fetchall()]

        return jsonify({
            "status": "success",
            "total_students": stat["total"],
            "avg_cgpa": round(float(stat["avg_cgpa"]), 2) if stat["avg_cgpa"] else 0.0,
            "department_counts": dept_counts,
            "engine": mode
        })
    finally:
        conn.close()


# =======================================================
# FRONTEND & STATIC ROUTING (UNIVERSAL FOR VERCEL & LOCAL)
# =======================================================
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    # 1. If path points to an actual file in public (like style.css, app.js), serve it
    file_path = os.path.join(PUBLIC_DIR, path)
    if path and os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(PUBLIC_DIR, path)

    # 2. Support /static/ prefix
    if path.startswith("static/"):
        sub_path = path[7:]
        static_file = os.path.join(PUBLIC_DIR, sub_path)
        if os.path.exists(static_file) and os.path.isfile(static_file):
            return send_from_directory(PUBLIC_DIR, sub_path)

    # 3. For any other path (including / and /api/index.py from Vercel), serve index.html
    return send_from_directory(PUBLIC_DIR, "index.html")


if __name__ == "__main__":
    print("====================================================")
    print("  Student Records Management System (DBMS CRUD App)")
    print("====================================================")
    init_database()
    print("\n* Web Application is running!")
    print("* Open in your browser: http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
