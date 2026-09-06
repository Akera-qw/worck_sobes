from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg
import json

app = FastAPI()

class TestResult(BaseModel):
    name: str
    passed: bool
    attempts: int
    last_response: dict

def get_conn():
    return psycopg.connect(host="127.0.0.1", port=5432, dbname="station", user="postgres", password="DB_PASSWORD")

@app.post("/results")
def post_results(test_result: TestResult):
    conn = get_conn()
    with conn .cursor() as cur:
        cur.execute(
            "INSERT INTO test_results (name, passed, attempts, last_response) VALUES (%s, %s, %s, %s)",
            (test_result.name, test_result.passed, test_result.attempts, json.dumps(test_result.last_response))
        )
    conn .commit()
    conn .close()
    return {"status": "saved"}

@app.get("/results")
def get_results():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, passed, attempts, last_response FROM test_results")
        rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "passed": r[2],
            "attempts": r[3],
            "last_response": r[4],
        })
    return result

@app.get("/results/{id}")
def get_results_id(id: int):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, passed, attempts, last_response FROM test_results WHERE id = %s", (id,))
        row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Результат не найден")
    result = {
        "id": row[0],
        "name": row[1],
        "passed": row[2],
        "attempts": row[3],
        "last_response": row[4],
    }
    return result
