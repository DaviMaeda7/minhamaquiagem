import sqlite3
from src.repositorios.repository import UserRepository, User

DB_PATH = "database.sqlite"

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT UNIQUE NOT NULL,
                username      TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entradas_diario (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                texto     TEXT    NOT NULL,
                criado_em TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()


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
        email_exists    = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone() is not None
        username_exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone() is not None
        conn.close()
        return {"email": email_exists, "username": username_exists}


class SQLiteDiarioRepository:
    def criar(self, user_id: int, texto: str) -> dict:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "INSERT INTO entradas_diario (user_id, texto) VALUES (?, ?)",
                (user_id, texto)
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, texto, criado_em FROM entradas_diario WHERE id = ?",
                (cur.lastrowid,)
            ).fetchone()
        return dict(row)

    def listar(self, user_id: int) -> list[dict]:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, texto, criado_em FROM entradas_diario "
                "WHERE user_id = ? ORDER BY id DESC",
                (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def apagar(self, entrada_id: int, user_id: int) -> bool:
        with sqlite3.connect(DB_PATH) as conn:
            affected = conn.execute(
                "DELETE FROM entradas_diario WHERE id = ? AND user_id = ?",
                (entrada_id, user_id)
            ).rowcount
            conn.commit()
        return affected > 0