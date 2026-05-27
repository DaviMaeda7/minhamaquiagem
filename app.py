from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from src.repositorios.sqlite_repository import init_db, SQLiteUserRepository, SQLiteDiarioRepository
from src.servicos.auth import hash_password, verify_password, validate_signup_data, validate_login_data

app = Flask(__name__)
app.secret_key = "chave-secreta-temporaria-para-testes-em-desenvolvimento"
CORS(app, supports_credentials=True, origins=[
    "https://minhamaquiagem.vidadavi777.workers.dev",
    "https://minhamaquiagem-production.up.railway.app"
])

init_db()
repo        = SQLiteUserRepository()
repo_diario = SQLiteDiarioRepository()

banco_dados = {
    "contatos": [
        {"nome": "Polícia",                        "telefone": "190"},
        {"nome": "Central de Atendimento à Mulher","telefone": "180"},
        {"nome": "SAMU",                           "telefone": "192"}
    ],
    "questionarios": []
}

# ── Páginas ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home-secret')
def homesecret():
    if 'user_id' not in session:
        return redirect('/login')
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
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('contatos.html')

@app.route('/diario')
def pagina_diario():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('diario.html')

@app.route('/questionario')
def pagina_questionario():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('questionario.html')

@app.route('/dados')
def pagina_dados():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dados.html')

@app.route('/localizacao')
def pagina_localizacao():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('localizacao.html')

@app.route('/home-visitor')
def home_visitor():
    return render_template('home-visitor.html')

# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/api/signup', methods=['POST'])
def api_signup():
    dados = request.get_json()
    erro = validate_signup_data(dados)
    if erro: return jsonify({"success": False, "message": erro}), 400
    exists = repo.exists(dados['email'], dados['username'])
    if exists['email']:    return jsonify({"success": False, "message": "Este e-mail já está cadastrado."}), 400
    if exists['username']: return jsonify({"success": False, "message": "Este nome de acesso já está em uso."}), 400
    senha_hash   = hash_password(dados['password'])
    novo_usuario = repo.create(dados['email'], dados['username'], senha_hash)
    session['user_id']  = novo_usuario.id
    session['username'] = novo_usuario.username
    return jsonify({"success": True, "message": "Conta criada com sucesso!"}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json()
    erro = validate_login_data(dados)
    if erro: return jsonify({"success": False, "message": erro}), 400
    usuario = repo.find_by_email(dados['email'])
    if not usuario or not verify_password(dados['password'], usuario.password_hash):
        return jsonify({"success": False, "message": "Dados incorretos. Verifique e tente novamente."}), 401
    session['user_id']  = usuario.id
    session['username'] = usuario.username
    return jsonify({"success": True}), 200

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True}), 200

# ── Diário ───────────────────────────────────────────────────────────────────

@app.route('/api/diario', methods=['GET'])
def listar_diario():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Não autenticada."}), 401
    return jsonify(repo_diario.listar(session['user_id'])), 200

@app.route('/api/diario', methods=['POST'])
def salvar_diario():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Não autenticada."}), 401
    dados = request.get_json(silent=True) or {}
    texto = (dados.get('texto') or '').strip()
    if not texto:
        return jsonify({"success": False, "message": "Texto não pode ser vazio."}), 400
    nova = repo_diario.criar(session['user_id'], texto)
    return jsonify({"success": True, "entrada": nova}), 201

@app.route('/api/diario/<int:entrada_id>', methods=['DELETE'])
def apagar_diario(entrada_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Não autenticada."}), 401
    if not repo_diario.apagar(entrada_id, session['user_id']):
        return jsonify({"success": False, "message": "Entrada não encontrada."}), 404
    return jsonify({"success": True}), 200

# ── Questionário ─────────────────────────────────────────────────────────────

@app.route('/api/questionario', methods=['POST'])
def salvar_questionario():
    dados = request.get_json()
    if dados.get('respostas'):
        banco_dados["questionarios"].append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "respostas": dados.get('respostas'),
            "nivel_risco_front": dados.get('nivel')
        })
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

# ── Contatos ─────────────────────────────────────────────────────────────────

@app.route('/api/contatos', methods=['GET'])
def listar_contatos():
    return jsonify(banco_dados["contatos"]), 200

@app.route('/api/contatos', methods=['POST'])
def adicionar_contato():
    dados = request.get_json()
    if dados.get('nome') and dados.get('telefone'):
        banco_dados["contatos"].append({"nome": dados.get('nome'), "telefone": dados.get('telefone')})
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400


if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))