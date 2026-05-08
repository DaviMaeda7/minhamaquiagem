from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)


banco_dados = {
    "diario": [],
    "contatos": [
        {"nome": "Polícia", "telefone": "190"},
        {"nome": "Central de Atendimento à Mulher", "telefone": "180"},
        {"nome": "SAMU", "telefone": "192"}
    ],
    "questionarios": []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home-secret')
def homesecret():
    return render_template('home_secret.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/novidades')
def novidades():
    return render_template('novidades.html')

@app.route('/make')
def make():
    return render_template('make.html')

@app.route('/skincare')
def skincare():
    return render_template('skincare.html')

@app.route('/favoritos')
def favoritos():
    return render_template('favoritos.html')

@app.route('/contatos')
def pagina_contatos():
    return render_template('contatos.html')

@app.route('/diario')
def pagina_diario():
    return render_template('diario.html')

@app.route('/questionario')
def pagina_questionario():
    return render_template('questionario.html')

@app.route('/dados')
def pagina_dados():
    return render_template('dados.html')

@app.route('/localizacao')
def pagina_localizacao():
    return render_template('localizacao.html')

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
        banco_dados["diario"].append({
            "texto": texto,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        print(f"Novo registro no diário: {texto}")
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

@app.route('/api/questionario', methods=['POST'])
def salvar_questionario():
    dados = request.get_json()
    respostas = dados.get('respostas')
    nivel = dados.get('nivel')
    if respostas:
        banco_dados["questionarios"].append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "respostas": respostas,
            "nivel_risco": nivel
        })
        print(f"Questionário respondido — nível de risco: {nivel}")
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

@app.route('/api/contatos', methods=['GET'])
def listar_contatos():
    return jsonify(banco_dados["contatos"]), 200

@app.route('/api/contatos', methods=['POST'])
def adicionar_contato():
    dados = request.get_json()
    nome = dados.get('nome')
    telefone = dados.get('telefone')
    if nome and telefone:
        banco_dados["contatos"].append({"nome": nome, "telefone": telefone})
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

    
if __name__ == '__main__':
    app.run(debug=True)