import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="station",
    user="postgres",
    password="secret",
)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            passed BOOLEAN NOT NULL,
            attempts INTEGER NOT NULL,
            last_response TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

conn.commit()
conn.close()

print("Таблица создана")