from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

def get_db_connection():
    return psycopg2.connect(
        dbname="startup_intel",
        user="startup",
        password="secret",
        host="postgres"
    )

@app.get("/startups")
def read_startups():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM startups ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]
