"""
kpi.py
─────────────────────────────────────────────────────────────
Gerenciador de métricas e eventos do sistema.
"""

def log_event(event_name: str, user_id: int = None):
    """
    Registra um evento para cálculo de KPI.
    No futuro, esta função fará um INSERT na tabela 'kpi_events' do SQLite.
    """
    user_info = f"Usuário ID: {user_id}" if user_id else "Usuário Anônimo"
    print(f"[📊 KPI REGISTRADA] Evento: {event_name} | {user_info}")