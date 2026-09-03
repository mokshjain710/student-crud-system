import json
import pymysql

try:
    with open("config.json", "r") as f:
        cfg = json.load(f)["mysql"]
    
    print(f"Connecting to MySQL on {cfg['host']}:{cfg['port']} as user '{cfg['user']}'...")
    conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"]
    )
    print("\n>>> [SUCCESS] Successfully connected to MySQL Server! <<<")
    with conn.cursor() as cur:
        cur.execute("SHOW DATABASES;")
        dbs = [row[0] for row in cur.fetchall()]
        print("Available Databases:", dbs)
    conn.close()
except pymysql.err.OperationalError as e:
    err_code, err_msg = e.args
    print(f"\n>>> [FAILED] MySQL Connection Error ({err_code}): {err_msg}")
    if err_code == 1045:
        print("\n--> REASON: Wrong or missing password for user 'root'.")
        print("--> FIX: What password do you enter when opening MySQL Workbench?")
        print("--> Put that exact password inside 'config.json' in the 'password' field.")
except Exception as e:
    print(f"\n>>> [ERROR]: {e}")
