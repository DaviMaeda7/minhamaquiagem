"""
questionnaire_routes.py
─────────────────────────────────────────────────────────────
Rota POST /questionnaire.

Separada em Blueprint para manter o app.py limpo conforme
o projeto crescer. Registre no app.py com:
    from questionnaire_routes import questionnaire_bp
    app.register_blueprint(questionnaire_bp)
"""

from flask import Blueprint, request, jsonify
from src.factory import get_questionnaire_repository, TOTAL_QUESTIONS
from src.servicos.questionnaire_service import QuestionnaireService

questionnaire_bp = Blueprint("questionnaire", __name__)


@questionnaire_bp.route("/questionnaire", methods=["POST"])
def submit_questionnaire():
    """
    Recebe e persiste as respostas do questionário de avaliação de risco.

    Corpo esperado (JSON):
    {
        "user_id": 1,
        "answers": {
            "1": "A",
            "2": "C",
            "3": "B",
            ...
        }
    }

    Todas as perguntas de 1 até TOTAL_QUESTIONS devem ser respondidas.
    Respostas válidas: "A", "B", "C" ou "D".

    Retorno em sucesso (201):
    {
        "message": "Respostas registradas com sucesso.",
        "submission_id": 42,
        "submitted_at": "2024-01-15 10:30:00"
    }
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Corpo da requisição inválido ou ausente."}), 400

    # Valida presença dos campos obrigatórios
    user_id = data.get("user_id")
    answers = data.get("answers")

    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "Campo 'user_id' obrigatório e deve ser um número inteiro."}), 422

    if answers is None:
        return jsonify({"error": "Campo 'answers' obrigatório."}), 422

    # Delega validação, persistência e encaminhamento ao serviço
    service = QuestionnaireService(
        repo=get_questionnaire_repository(),
        total_questions=TOTAL_QUESTIONS,
    )

    try:
        result = service.submit(user_id=user_id, raw_answers=answers)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    return jsonify({
        "message": "Respostas registradas com sucesso.",
        **result,
    }), 201
