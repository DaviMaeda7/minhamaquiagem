"""
sqlite_repository.py
Implementação do banco de dados local (SQLite) para Usuários.
"""
import sqlite3
from src.repositorios.repository import UserRepository, User

DB_PATH = "database.sqlite"

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_connection()
    # Cria a tabela de usuários
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

class SQLiteUserRepository(UserRepository):
    def create(self, email: str, username: str, password_hash: bytes) -> User:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
            (email, username, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return User(id=user_id, email=email, username=username, password_hash=password_hash)

    def find_by_email(self, email: str) -> User | None:
        conn = _get_connection()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if row:
            return User(id=row["id"], email=row["email"], username=row["username"], password_hash=row["password_hash"])
        return None

    def exists(self, email: str, username: str) -> dict:
        conn = _get_connection()
        email_exists = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone() is not None
        username_exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone() is not None
        conn.close()
        return {"email": email_exists, "username": username_exists}