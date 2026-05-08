from flask import Flask, render_template, request, jsonify, session, redirect
from datetime import datetime

# Importando a segurança e o banco de dados local que configuramos
from src.repositorios.sqlite_repository import init_db, SQLiteUserRepository
from src.servicos.auth import hash_password, verify_password, validate_signup_data, validate_login_data

app = Flask(__name__)
# Chave necessária para manter o login da usuária ativo (sessão)
app.secret_key = "chave-secreta-temporaria-para-testes-em-desenvolvimento"

# Inicializa o banco de dados SQLite
init_db()
repo = SQLiteUserRepository()

banco_dados = {
    "diario": [],
    "contatos": [
        {"nome": "Polícia", "telefone": "190"},
        {"nome": "Central de Atendimento à Mulher", "telefone": "180"},
        {"nome": "SAMU", "telefone": "192"}
    ],
    "questionarios": []
}

# =============================================
# ROTAS DE NAVEGAÇÃO (PÁGINAS HTML)
# =============================================

@app.route('/')
def index():
    # A pedido, o app agora inicia direto na tela de login
    return redirect('/login')

@app.route('/loja')
def loja():
    # A fachada da loja (index.html) foi movida para cá temporariamente
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# --- NOVAS ROTAS DA FACHADA (LOJA) ---

@app.route('/skincare')
def pagina_skincare():
    return render_template('skincare.html')

@app.route('/make')
def pagina_make():
    return render_template('make.html')

@app.route('/novidades')
def pagina_novidades():
    return render_template('novidades.html')

@app.route('/favoritos')
def pagina_favoritos():
    return render_template('favoritos.html')

# --- ROTAS DA ÁREA SECRETA (PROTEGIDAS) ---

@app.route('/home-secret')
def home_secret():
    # Se não houver ninguém logado, expulsa para o login
    if 'user_id' not in session: return redirect('/login')
    return render_template('home_secret.html')

@app.route('/localizacao')
def pagina_localizacao():
    if 'user_id' not in session: return redirect('/login')
    return render_template('localizacao.html')

@app.route('/contatos')
def pagina_contatos():
    if 'user_id' not in session: return redirect('/login')
    return render_template('contatos.html')

@app.route('/diario')
def pagina_diario():
    if 'user_id' not in session: return redirect('/login')
    return render_template('diario.html')

@app.route('/questionario')
def pagina_questionario():
    if 'user_id' not in session: return redirect('/login')
    return render_template('questionario.html')

@app.route('/dados')
def pagina_dados():
    if 'user_id' not in session: return redirect('/login')
    return render_template('dados.html')

# =============================================
# ROTAS DE API (AUTENTICAÇÃO E DADOS)
# =============================================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    dados = request.get_json()
    erro = validate_signup_data(dados)
    if erro: return jsonify({"success": False, "message": erro}), 400
        
    exists = repo.exists(dados['email'], dados['username'])
    if exists['email']: return jsonify({"success": False, "message": "Este e-mail já está cadastrado."}), 400
    if exists['username']: return jsonify({"success": False, "message": "Este nome de acesso já está em uso."}), 400
        
    senha_hash = hash_password(dados['password'])
    novo_usuario = repo.create(dados['email'], dados['username'], senha_hash)
    
    session['user_id'] = novo_usuario.id
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
        
    session['user_id'] = usuario.id
    session['username'] = usuario.username
    return jsonify({"success": True}), 200

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True}), 200

@app.route('/api/diario', methods=['POST'])
def salvar_diario():
    dados = request.get_json()
    texto = dados.get('texto')
    if texto:
        banco_dados["diario"].append({"texto": texto, "data": datetime.now().strftime("%d/%m/%Y %H:%M")})
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

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
    app.run(debug=True)