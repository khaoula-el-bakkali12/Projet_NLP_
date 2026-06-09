import os
import json
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["history"])

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "oncologia.db")


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id       TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                question TEXT NOT NULL,
                answer   TEXT NOT NULL,
                model    TEXT,
                sources  TEXT DEFAULT '[]'
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_user ON history(username, timestamp DESC)"
        )
        conn.commit()


_init_db()


# ── Pydantic models ──────────────────────────────────────────────────────────

class HistorySource(BaseModel):
    id: Optional[str] = None
    titre: Optional[str] = None
    categorie: Optional[str] = None
    type_cancer: Optional[str] = None
    score_final: Optional[float] = None
    reference: Optional[str] = None


class HistoryItem(BaseModel):
    id: str
    timestamp: str
    question: str
    answer: str
    model: str
    sources: List[HistorySource] = []


class SaveHistoryRequest(BaseModel):
    username: str
    item: HistoryItem


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/history")
def get_history(username: str):
    """Return all history items for a user, newest first."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM history WHERE username = ? ORDER BY timestamp DESC",
            (username,),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["sources"] = json.loads(item.get("sources") or "[]")
        result.append(item)
    return result


@router.post("/history")
def save_history_item(req: SaveHistoryRequest):
    """Persist one Q&A item for a user (idempotent by id)."""
    item = req.item
    sources_json = json.dumps(
        [s.model_dump(exclude_none=True) for s in item.sources],
        ensure_ascii=False,
    )
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO history (id, username, timestamp, question, answer, model, sources)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (item.id, req.username, item.timestamp, item.question, item.answer, item.model, sources_json),
        )
        conn.commit()
    return {"status": "saved"}


@router.delete("/history/{item_id}")
def delete_history_item(item_id: str, username: str):
    """Remove one history item."""
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM history WHERE id = ? AND username = ?",
            (item_id, username),
        )
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found.")
    return {"status": "deleted"}


@router.delete("/history")
def clear_history(username: str):
    """Delete all history for a user."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM history WHERE username = ?", (username,))
        conn.commit()
    return {"status": "cleared"}
