from flask import Flask, render_template, request, jsonify

# Como o arquivo se chama quiz.py e está na mesma pasta, a importação fica assim:
from quiz import calcular_resultado_quiz

app = Flask(__name__)

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
    return render_template('index.html')

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
# ROTAS DO QUIZ
# =============================================

@app.route('/quiz')
def pagina_quiz():
    return render_template('quiz.html')

@app.route('/submit-quiz', methods=['POST'])
def processar_quiz():
    try:
        # Pega as 6 respostas do formulário HTML
        respostas = [
            int(request.form.get('q1')),
            int(request.form.get('q2')),
            int(request.form.get('q3')),
            int(request.form.get('q4')),
            int(request.form.get('q5')),
            int(request.form.get('q6'))
        ]
        
        # Chama a função do seu arquivo quiz.py
        resultado = calcular_resultado_quiz(respostas)
        
        # Envia os resultados para a tela final
        return render_template('resultado_quiz.html', resultado=resultado)
    
    except (TypeError, ValueError):
        return "Erro: Por favor, responda a todas as perguntas corretamente antes de enviar.", 400

# =============================================
# ROTAS DE API (PROCESSAMENTO DE DADOS)
# =============================================

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