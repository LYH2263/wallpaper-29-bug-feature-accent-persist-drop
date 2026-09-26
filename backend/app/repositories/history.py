import json
from datetime import datetime, timezone

from app.db import connect


def insert_run(wall_id: int, roll_id: int, result: dict, note: str = "") -> int:
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (wall_id, roll_id, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_runs(limit: int = 50, wall_id: int | None = None):
    conn = connect()
    try:
        sql = """
            SELECT r.*, w.name wall_name, rl.name roll_name
            FROM calc_runs r
            LEFT JOIN walls w ON w.id=r.wall_id
            LEFT JOIN rolls rl ON rl.id=r.roll_id
        """
        params: list = []
        if wall_id is not None:
            sql += " WHERE r.wall_id = ?"
            params.append(wall_id)
        sql += " ORDER BY r.id DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        from app.services.feature_persist import list_summary_view, open_detail_view

        out = []
        for row in rows:
            d = dict(row)
            raw = json.loads(d.pop("result_json"))
            # List open collapses accent rolls; side keys may still hold prior figures.
            shaped = list_summary_view(raw)
            d["result"] = open_detail_view(shaped)
            out.append(d)
        return out
    finally:
        conn.close()
