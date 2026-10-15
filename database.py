
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "peerfin.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                borrower TEXT NOT NULL,
                amount REAL NOT NULL,
                purpose TEXT NOT NULL,
                duration INTEGER NOT NULL,
                risk INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                interest_rate REAL NOT NULL DEFAULT 10.0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS funding_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                borrower TEXT NOT NULL,
                loan_amount REAL NOT NULL,
                amount REAL NOT NULL,
                purpose TEXT NOT NULL,
                note TEXT NOT NULL
            )
        """)

        columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(applications)"
            ).fetchall()
        ]

        if "interest_rate" not in columns:
            conn.execute("""
                ALTER TABLE applications
                ADD COLUMN interest_rate REAL NOT NULL DEFAULT 10.0
            """)

def load_applications():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, borrower, amount, purpose,
                   duration, risk, status, interest_rate
            FROM applications
            ORDER BY id
        """).fetchall()

    return [
        {
            "id": row[0],
            "borrower": row[1],
            "amount": row[2],
            "purpose": row[3],
            "duration": row[4],
            "risk": row[5],
            "status": row[6],
            "interest_rate": row[7],
        }
        for row in rows
    ]


def save_application(application):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO applications
            (borrower, amount, purpose, duration, risk,
             status, interest_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            application["borrower"],
            application["amount"],
            application["purpose"],
            application["duration"],
            application["risk"],
            application.get("status", "Pending"),
            application.get("interest_rate", 10.0),
        ))

        return cursor.lastrowid


def update_application_status(application_id, status):
    with get_connection() as conn:
        conn.execute("""
            UPDATE applications
            SET status = ?
            WHERE id = ?
        """, (status, application_id))

def save_interest_rate(application_id, interest_rate):
    with get_connection() as conn:
        conn.execute("""
            UPDATE applications
            SET interest_rate = ?
            WHERE id = ?
        """, (interest_rate, application_id))
        
def load_funding_records():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, application_id, borrower,
                   loan_amount, amount, purpose, note
            FROM funding_records
            ORDER BY id
        """).fetchall()

    return [
        {
            "ID": row[0],
            "Application ID": row[1],
            "Borrower": row[2],
            "Loan Amount": row[3],
            "Amount": row[4],
            "Purpose": row[5],
            "Note": row[6],
        }
        for row in rows
    ]


def save_funding_record(record):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO funding_records
            (application_id, borrower, loan_amount,
             amount, purpose, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            record["Application ID"],
            record["Borrower"],
            record["Loan Amount"],
            record["Amount"],
            record["Purpose"],
            record["Note"],
        ))



def save_repayment(repayment):
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repayments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                borrower TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT NOT NULL
            )
        """)

        conn.execute("""
            INSERT INTO repayments
            (application_id, borrower, amount, note)
            VALUES (?, ?, ?, ?)
        """, (
            repayment["Application ID"],
            repayment["Borrower"],
            repayment["Amount"],
            repayment["Note"]
        ))

def load_repayments():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repayments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                borrower TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT NOT NULL
            )
        """)

        rows = conn.execute("""
            SELECT id, application_id, borrower, amount, note
            FROM repayments
            ORDER BY id DESC
        """).fetchall()

    return [
        {
            "ID": row[0],
            "Application ID": row[1],
            "Borrower": row[2],
            "Amount": row[3],
            "Note": row[4]
        }
        for row in rows
    ]

def reset_database():
    with get_connection() as conn:
        conn.execute("DELETE FROM repayments")
        conn.execute("DELETE FROM funding_records")
        conn.execute("DELETE FROM applications")

        # Reset auto-increment IDs
        conn.execute("""
            DELETE FROM sqlite_sequence
            WHERE name IN (
                'repayments',
                'funding_records',
                'applications'
            )
        """)
