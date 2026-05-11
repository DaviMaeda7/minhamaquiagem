import os
from src.repositorios.repository import UserRepository
from src.repositorios.questionnaire_repository import QuestionnaireRepository

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")
TOTAL_QUESTIONS = int(os.getenv("TOTAL_QUESTIONS", "10"))

def get_user_repository() -> UserRepository:
    if DB_BACKEND == "sqlite":
        from src.repositorios.sqlite_repository import SQLiteUserRepository, init_db
        init_db()
        return SQLiteUserRepository()
    raise ValueError(f"DB_BACKEND desconhecido: '{DB_BACKEND}'")

def get_questionnaire_repository() -> QuestionnaireRepository:
    if DB_BACKEND == "sqlite":
        from src.repositorios.sqlite_questionnaire_repository import (
            SQLiteQuestionnaireRepository,
            init_questionnaire_table,
        )
        init_questionnaire_table()
        return SQLiteQuestionnaireRepository()
    raise ValueError(f"DB_BACKEND desconhecido: '{DB_BACKEND}'")