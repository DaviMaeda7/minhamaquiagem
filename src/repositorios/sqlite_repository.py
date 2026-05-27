"""
sqlite_repository.py  (na prática: repositório PostgreSQL)
─────────────────────────────────────────────────────────────
Implementação concreta dos repositórios usando PostgreSQL via psycopg2.
O nome do arquivo é legado — o banco real é Postgres.
"""

import os
import psycopg2
import psycopg2.extras
from src.repositorios.repository import UserRepository, User


def _get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")


def init_db():
    """Cria todas as tabelas necessárias caso ainda não existam."""
    with _get_connection() as conn:
        with conn.cursor() as cur:

            # Usuários
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            SERIAL PRIMARY KEY,
                    email         TEXT UNIQUE NOT NULL,
                    username      TEXT UNIQUE NOT NULL,
                    password_hash BYTEA NOT NULL
                )
            """)

            # Diário
            cur.execute("""
                CREATE TABLE IF NOT EXISTS entradas_diario (
                    id        SERIAL PRIMARY KEY,
                    user_id   INTEGER NOT NULL,
                    texto     TEXT NOT NULL,
                    criado_em TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # ── KPI ────────────────────────────────────────────────────────────
            # Tabela de eventos. Cada linha = uma ação registrada no sistema.
            # user_id é NULL para eventos anônimos (ex.: signup antes do login).
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kpi_events (
                    id        SERIAL PRIMARY KEY,
                    event     TEXT NOT NULL,
                    user_id   INTEGER,
                    criado_em TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)

        conn.commit()


# ── Usuários ──────────────────────────────────────────────────────────────────

class SQLiteUserRepository(UserRepository):

    def create(self, email: str, username: str, password_hash: bytes) -> User:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (email, username, password_hash) VALUES (%s, %s, %s) RETURNING id",
                    (email, username, psycopg2.Binary(password_hash))
                )
                user_id = cur.fetchone()[0]
            conn.commit()
        return User(id=user_id, email=email, username=username, password_hash=password_hash)

    def find_by_email(self, email: str) -> User | None:
        with _get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
        if row:
            return User(
                id=row["id"],
                email=row["email"],
                username=row["username"],
                password_hash=bytes(row["password_hash"]),
            )
        return None

    def exists(self, email: str, username: str) -> dict:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
                email_exists = cur.fetchone() is not None
                cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
                username_exists = cur.fetchone() is not None
        return {"email": email_exists, "username": username_exists}


# ── Diário ────────────────────────────────────────────────────────────────────

class SQLiteDiarioRepository:

    def criar(self, user_id: int, texto: str) -> dict:
        with _get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO entradas_diario (user_id, texto) VALUES (%s, %s) RETURNING id, texto, criado_em",
                    (user_id, texto)
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row)

    def listar(self, user_id: int) -> list[dict]:
        with _get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, texto, criado_em FROM entradas_diario WHERE user_id = %s ORDER BY id DESC",
                    (user_id,)
                )
                rows = cur.fetchall()
        return [dict(r) for r in rows]

    def apagar(self, entrada_id: int, user_id: int) -> bool:
        with _get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM entradas_diario WHERE id = %s AND user_id = %s",
                    (entrada_id, user_id)
                )
                affected = cur.rowcount
            conn.commit()
        return affected > 0