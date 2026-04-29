from flask import Flask, render_template, request, jsonify
from quiz_service import calcular_resultado_quiz

app = Flask(__name__)

# =============================================
# CONFIGURAÇÃO DO QUIZ
# Mude aqui o nome do template onde o popup
# do quiz está embutido, se necessário.
# =============================================

PAGINA_COM_QUIZ = 'index.html'

# Banco de dados temporário
banco_dados = {
    "diario": [],
    "contatos": [
        {"nome": "Emergência 1", "telefone": "190"},
        {"nome": "Contato de Confiança", "telefone": "(11) 99999-9999"}
    ]
}

# =============================================
# ROTAS DE NAVEGAÇÃO (PÁGINAS HTML)
# =============================================

@app.route('/')
def index():
    return render_template(PAGINA_COM_QUIZ)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home-secret')
def home_secret():
    return render_template('home_secret.html')

@app.route('/localizacao')
def pagina_localizacao():
    return render_template('localizacao.html')

@app.route('/contanto')
def pagina_contatos():
    return render_template('contanto.html')

@app.route('/diario')
def pagina_diario():
    return render_template('diario.html')

# =============================================
# ROTAS DE API (PROCESSAMENTO DE DADOS)
# =============================================

@app.route('/api/quiz', methods=['POST'])
def processar_quiz():
    """
    Recebe as respostas do quiz via JSON e devolve o resultado calculado.

    Corpo esperado:
    { "respostas": [0, 2, 1, 3, 0, 1] }
    — lista com 6 inteiros (0 a 3), um por pergunta, na ordem.

    Retorno em sucesso (200):
    {
        "pontuacoes": { "fisica": 5, "emocional": 8, "patrimonial": 3 },
        "niveis_risco": {
            "fisica":      { "label": "Moderado", "cor": "amarelo" },
            "emocional":   { "label": "Alto",     "cor": "vermelho" },
            "patrimonial": { "label": "Baixo",    "cor": "verde"    }
        },
        "perfil_predominante": {
            "nome": "...",
            "descricao": "...",
            "recomendacoes": [...]
        }
    }
    """
    dados = request.get_json(silent=True)

    if not dados or "respostas" not in dados:
        return jsonify({"erro": "Campo 'respostas' obrigatório."}), 400

    respostas = dados["respostas"]

    if not isinstance(respostas, list) or len(respostas) != 6:
        return jsonify({"erro": "'respostas' deve ser uma lista com exatamente 6 itens."}), 400

    if not all(isinstance(r, int) and 0 <= r <= 3 for r in respostas):
        return jsonify({"erro": "Cada resposta deve ser um número inteiro entre 0 e 3."}), 400

    resultado = calcular_resultado_quiz(respostas)
    return jsonify(resultado), 200


@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json()
    if dados.get('senha') == 'segura123':
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "message": "Senha incorreta"}), 401

@app.route('/api/diario', methods=['POST'])
def salvar_diario():
    dados = request.get_json()
    texto = dados.get('texto')
    if texto:
        banco_dados["diario"].append(texto)
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400


if __name__ == '__main__':
    app.run(debug=True)