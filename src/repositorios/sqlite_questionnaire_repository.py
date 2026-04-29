"""
sqlite_questionnaire_repository.py
─────────────────────────────────────────────────────────────
Implementação SQLite do QuestionnaireRepository.

SEGURANÇA — criptografia em repouso:
  As respostas nunca são gravadas em texto puro no banco.
  Usamos Fernet (AES-128-CBC + HMAC-SHA256) da biblioteca
  cryptography. A chave vem da variável de ambiente
  QUESTIONNAIRE_SECRET_KEY.

  Gere a chave uma única vez com:
      python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  e salve em .env (nunca no repositório git).
"""

import json
import os
import sqlite3
from datetime import datetime
from cryptography.fernet import Fernet
from src.repositorios.questionnaire_repository import QuestionnaireRepository, QuestionnaireSubmission
from src.repositorios.sqlite_repository import _get_connection 


# ── Chave de criptografia ──────────────────────────────────────────────────────

def _get_fernet() -> Fernet:
    key = os.getenv("QUESTIONNAIRE_SECRET_KEY")
    if not key:
        raise EnvironmentError(
            "Variável de ambiente QUESTIONNAIRE_SECRET_KEY não definida. "
            "Gere uma chave com: python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def _encrypt(data: dict) -> str:
    """Serializa o dicionário de respostas e criptografa."""
    f = _get_fernet()
    return f.encrypt(json.dumps(data).encode()).decode()


def _decrypt(token: str) -> dict:
    """Descriptografa e desserializa o dicionário de respostas."""
    f = _get_fernet()
    try:
        return json.loads(f.decrypt(token.encode()))
    except InvalidToken:
        raise ValueError("Falha ao descriptografar respostas — token inválido ou chave incorreta.")


# ── Inicialização da tabela ────────────────────────────────────────────────────

def init_questionnaire_table() -> None:
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questionnaire_submissions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            answers_encrypted TEXT   NOT NULL,
            submitted_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


# ── Implementação ──────────────────────────────────────────────────────────────

class SQLiteQuestionnaireRepository(QuestionnaireRepository):

    def save(self, submission: QuestionnaireSubmission) -> QuestionnaireSubmission:
        encrypted = _encrypt(submission.answers)
        conn = _get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO questionnaire_submissions (user_id, answers_encrypted)
                VALUES (?, ?)
                """,
                (submission.user_id, encrypted),
            )
            conn.commit()

            # Busca a linha recém-criada para preencher id e submitted_at
            row = conn.execute(
                "SELECT id, submitted_at FROM questionnaire_submissions WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

            submission.id           = row["id"]
            submission.submitted_at = row["submitted_at"]
            return submission
        finally:
            conn.close()

    def find_by_user(self, user_id: int) -> list[QuestionnaireSubmission]:
        conn = _get_connection()
        try:
            rows = conn.execute(
                """
                SELECT id, user_id, answers_encrypted, submitted_at
                FROM questionnaire_submissions
                WHERE user_id = ?
                ORDER BY submitted_at DESC
                """,
                (user_id,),
            ).fetchall()

            return [
                QuestionnaireSubmission(
                    id=row["id"],
                    user_id=row["user_id"],
                    answers=_decrypt(row["answers_encrypted"]),
                    submitted_at=row["submitted_at"],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def find_latest_by_user(self, user_id: int) -> QuestionnaireSubmission | None:
        conn = _get_connection()
        try:
            row = conn.execute(
                """
                SELECT id, user_id, answers_encrypted, submitted_at
                FROM questionnaire_submissions
                WHERE user_id = ?
                ORDER BY submitted_at DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()

            if not row:
                return None

            return QuestionnaireSubmission(
                id=row["id"],
                user_id=row["user_id"],
                answers=_decrypt(row["answers_encrypted"]),
                submitted_at=row["submitted_at"],
            )
        finally:
            conn.close()
