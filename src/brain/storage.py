import sqlite3
import os
from icecream import ic

class AlertStorage:
    def __init__(self, db_path="alerts.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS high_risk_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_ip TEXT,
                dst_ip TEXT,
                src_port INTEGER,
                dst_port INTEGER,
                proto TEXT,
                score REAL,
                timestamp INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        ic(f"SQLite database initialized at {self.db_path}")

    def save_alert(self, flow: dict, score: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO high_risk_flows (src_ip, dst_ip, src_port, dst_port, proto, score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            flow.get("src_ip"),
            flow.get("dst_ip"),
            flow.get("src_port"),
            flow.get("dst_port"),
            flow.get("proto"),
            score,
            flow.get("timestamp")
        ))
        conn.commit()
        conn.close()
        ic(f"Alert saved: {flow.get('src_ip')} -> {flow.get('dst_ip')} Score: {score}")
