"""
questionnaire_service.py
─────────────────────────────────────────────────────────────
Camada de serviço do questionário.

Responsabilidades:
  1. Validar as respostas recebidas pelo POST.
  2. Persistir via repositório (banco agnóstico).
  3. Entregar as respostas ao módulo de cálculo de perigo
     quando ele estiver pronto — hoje retorna os dados brutos.

Esse arquivo é o ponto de conexão entre a rota HTTP e a
lógica de negócio. A rota não precisa saber como as respostas
são validadas nem como o perigo é calculado.
"""

from src.repositorios.questionnaire_repository import QuestionnaireRepository, QuestionnaireSubmission

VALID_OPTIONS = {"A", "B", "C", "D"}

# ── Validação ──────────────────────────────────────────────────────────────────

def validate_answers(answers: dict, total_questions: int) -> str | None:
    """
    Valida o dicionário de respostas recebido.

    answers deve ser:  { "1": "A", "2": "C", ... }
    (as chaves chegam como string do JSON e são convertidas para int aqui)

    Retorna mensagem de erro (str) ou None se tudo estiver correto.
    """
    if not isinstance(answers, dict) or not answers:
        return "O campo 'answers' deve ser um objeto não vazio."

    expected_ids = set(range(1, total_questions + 1))
    received_ids = set()

    for key, value in answers.items():
        # Chaves precisam ser números inteiros (podem chegar como string via JSON)
        if not str(key).isdigit():
            return f"ID de pergunta inválido: '{key}'. Use somente números inteiros."
        q_id = int(key)
        received_ids.add(q_id)

        if value not in VALID_OPTIONS:
            return (
                f"Resposta inválida '{value}' para a pergunta {q_id}. "
                f"Opções válidas: {sorted(VALID_OPTIONS)}."
            )

    missing = expected_ids - received_ids
    if missing:
        return f"Perguntas sem resposta: {sorted(missing)}."

    extra = received_ids - expected_ids
    if extra:
        return f"IDs de pergunta inexistentes: {sorted(extra)}."

    return None


# ── Serviço ────────────────────────────────────────────────────────────────────

class QuestionnaireService:

    def __init__(self, repo: QuestionnaireRepository, total_questions: int):
        self.repo             = repo
        self.total_questions  = total_questions

    def submit(self, user_id: int, raw_answers: dict) -> dict:
        """
        Valida, persiste e encaminha as respostas.

        Retorna um dicionário pronto para ser enviado como resposta JSON:
          - Em sucesso: { "submission_id": int, "submitted_at": str }
          - Com erro:   lança ValueError com a mensagem

        Quando o módulo de cálculo de perigo estiver pronto, basta
        chamar danger_calculator.evaluate(submission) aqui, após o save.
        """
        error = validate_answers(raw_answers, self.total_questions)
        if error:
            raise ValueError(error)

        # Normaliza chaves para int antes de persistir
        normalized = {int(k): v for k, v in raw_answers.items()}

        submission = self.repo.save(
            QuestionnaireSubmission(user_id=user_id, answers=normalized)
        )

        # ── Ponto de extensão ──────────────────────────────────────────────────
        # Quando o módulo de cálculo estiver pronto, descomente:
        #
        # from danger_calculator import evaluate
        # danger_result = evaluate(submission)
        # return { ..., "danger_level": danger_result }
        # ──────────────────────────────────────────────────────────────────────

        return {
            "submission_id": submission.id,
            "submitted_at":  str(submission.submitted_at),
        }
