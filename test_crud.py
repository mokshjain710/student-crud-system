import json
from app import app, init_database

def test_full_crud_cycle():
    print("[1] Initializing database...")
    init_database()

    client = app.test_client()

    print("\n[2] Testing GET / (Frontend delivery)...")
    res = client.get('/')
    assert res.status_code == 200
    assert b"Student Management System" in res.data
    print("    -> PASS: Frontend loaded properly.")

    print("\n[3] Testing READ (GET /api/students)...")
    res = client.get('/api/students')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    initial_count = len(data["data"])
    print(f"    -> PASS: Retrieved {initial_count} records (Engine: {data.get('engine')}).")

    print("\n[4] Testing CREATE (POST /api/students)...")
    new_student = {
        "roll_no": "TEST999",
        "name": "Test Student",
        "email": "test.student@example.com",
        "department": "Computer Science",
        "semester": 5,
        "cgpa": 9.5
    }
    res = client.post('/api/students', data=json.dumps(new_student), content_type="application/json")
    assert res.status_code == 201
    created = res.get_json()
    student_id = created["id"]
    print(f"    -> PASS: Created student ID {student_id}.")

    print("\n[5] Testing READ single (GET /api/students/<id>)...")
    res = client.get(f'/api/students/{student_id}')
    assert res.status_code == 200
    s_data = res.get_json()["data"]
    assert s_data["roll_no"] == "TEST999"
    assert s_data["name"] == "Test Student"
    print("    -> PASS: Single student retrieved correctly.")

    print("\n[6] Testing UPDATE (PUT /api/students/<id>)...")
    update_data = {
        "roll_no": "TEST999",
        "name": "Updated Test Student",
        "email": "updated.student@example.com",
        "department": "Information Technology",
        "semester": 6,
        "cgpa": 9.85
    }
    res = client.put(f'/api/students/{student_id}', data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 200
    print("    -> PASS: Student updated successfully.")

    # Verify update
    res = client.get(f'/api/students/{student_id}')
    assert res.get_json()["data"]["name"] == "Updated Test Student"
    assert res.get_json()["data"]["department"] == "Information Technology"

    print("\n[7] Testing DELETE (DELETE /api/students/<id>)...")
    res = client.delete(f'/api/students/{student_id}')
    assert res.status_code == 200
    print("    -> PASS: Student deleted successfully.")

    # Verify deletion
    res = client.get(f'/api/students/{student_id}')
    assert res.status_code == 404
    print("    -> PASS: Confirmed deletion (returns 404).")

    print("\n[8] Testing STATS (GET /api/stats)...")
    res = client.get('/api/stats')
    assert res.status_code == 200
    stats = res.get_json()
    print(f"    -> PASS: Stats retrieved (Total: {stats['total_students']}, Avg CGPA: {stats['avg_cgpa']}).")

    print("\n>>> ALL CRUD TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_full_crud_cycle()
