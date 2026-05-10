from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "news.db")

app = FastAPI(title="News Reporter Backend")

# DB Initialization
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS newsletters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed INTEGER DEFAULT 0
            )
        """)
    print(f"Database initialized at {DB_PATH}")

init_db()

class NewsPayload(BaseModel):
    text: str

@app.post("/webhook")
async def receive_news(payload: NewsPayload):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO newsletters (content) VALUES (?)", 
                (payload.text,)
            )
            conn.commit()
            news_id = cursor.lastrowid
        return {"status": "success", "id": news_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news")
async def get_news():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM newsletters ORDER BY received_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
