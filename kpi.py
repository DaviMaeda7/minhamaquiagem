"""
src/servicos/kpi.py
─────────────────────────────────────────────────────────────
Registro de eventos de KPI no banco de dados.

COMO USAR:
    from src.servicos.kpi import log_event, KPI

    log_event(KPI.USER_LOGIN, user_id=3)

COMO ADICIONAR UM NOVO EVENTO:
    1. Adicione uma constante na classe KPI abaixo.
    2. Chame log_event(KPI.SUA_CONSTANTE) onde quiser registrar.
    Nenhum outro arquivo precisa ser alterado.

TABELA NO BANCO (criada pelo init_db em sqlite_repository.py):
    kpi_events (id, event, user_id, criado_em)
"""

import os
import psycopg2


# ── Catálogo de eventos ────────────────────────────────────────────────────────
# Todas as KPIs disponíveis ficam aqui.
# Altere ou adicione constantes livremente — são apenas strings.

class KPI:
    # Autenticação
    USER_SIGNUP  = "USER_SIGNUP"
    USER_LOGIN   = "USER_LOGIN"
    USER_LOGOUT  = "USER_LOGOUT"

    # Diário
    DIARIO_ENTRY_CREATED = "DIARIO_ENTRY_CREATED"
    DIARIO_ENTRY_DELETED = "DIARIO_ENTRY_DELETED"

    # Questionário
    QUESTIONNAIRE_FINISHED = "QUESTIONNAIRE_FINISHED"

    # Contatos
    CONTACT_ADDED = "CONTACT_ADDED"


# ── Função principal ───────────────────────────────────────────────────────────

def log_event(event_name: str, user_id: int = None) -> None:
    """
    Grava um evento de KPI no banco de dados.

    Parâmetros:
        event_name  — use uma das constantes de KPI (ex.: KPI.USER_LOGIN)
        user_id     — ID do usuário autenticado, ou None para ações anônimas
    """
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO kpi_events (event, user_id) VALUES (%s, %s)",
                    (event_name, user_id),
                )
        conn.close()
    except Exception as e:
        # KPI nunca deve quebrar o fluxo principal da aplicação
        print(f"[KPI] Falha ao registrar '{event_name}': {e}")