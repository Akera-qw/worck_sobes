import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="station",
    user="postgres",
    password="DB_PASSWORD",
)

with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO test_results (name, passed, attempts, last_response) VALUES (%s, %s, %s, %s)",
        ("Проверка связи", True, 1, "{'result': 'PONG'}"),
    )

    cur.execute("SELECT id, name, passed, attempts FROM test_results")
    rows = cur.fetchall()
    for row in rows:
        print(row)

conn.commit()
conn.close()
