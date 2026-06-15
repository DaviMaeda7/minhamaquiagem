from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import requests
import base64
import os
import cv2
import numpy as np

from src.repositorios.sqlite_repository import init_db, SQLiteUserRepository, SQLiteDiarioRepository
from src.servicos.auth import hash_password, verify_password, validate_signup_data, validate_login_data


app = Flask(__name__)
app.config.update(
    SECRET_KEY="chave-secreta-temporaria-para-testes-em-desenvolvimento",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

CORS(app, supports_credentials=True)

init_db()
repo        = SQLiteUserRepository()
repo_diario = SQLiteDiarioRepository()

banco_dados = {
    "contatos": [
        {"nome": "Polícia", "telefone": "190"},
        {"nome": "Central de Atendimento à Mulher", "telefone": "180"},
        {"nome": "SAMU", "telefone": "192"}
    ],
    "questionarios": []
}

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"

headers = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}"
}

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
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

@app.route('/chat-box')
def chat_box():
    return render_template('chat-box.html')

@app.route('/quizmake')
def quizmake():
    return render_template('quizmake.html')

@app.route('/tom-de-pele')
def tom_de_pele():
    return render_template('tom-de-pele.html')
# ── Inspirações ─────────────────────────────────────────────────────────────

@app.route('/inspiracoes')
def inspiracoes():
    return render_template('inspiracoes.html')

@app.route('/inspiracoes/easy')
def inspiracoes_easy():
    return render_template('easy.html')

@app.route('/inspiracoes/natural')
def inspiracoes_natural():
    return render_template('natural.html')

@app.route('/inspiracoes/soft-glam')
def inspiracoes_soft_glam():
    return render_template('soft.html')

@app.route('/inspiracoes/full-glam')
def inspiracoes_full_glam():
    return render_template('full.html')

@app.route('/inspiracoes/criativa')
def inspiracoes_criativa():
    return render_template('criativa.html')

# ── Outras páginas protegidas ───────────────────────────────────────────────

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

# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/api/signup', methods=['POST'])
def api_signup():
    dados = request.get_json()
    erro = validate_signup_data(dados)
    if erro:
        return jsonify({"success": False, "message": erro}), 400

    exists = repo.exists(dados['email'], dados['username'])
    if exists['email']:
        return jsonify({"success": False, "message": "Este e-mail já está cadastrado."}), 400
    if exists['username']:
        return jsonify({"success": False, "message": "Este nome de acesso já está em uso."}), 400

    senha_hash = hash_password(dados['password'])
    novo_usuario = repo.create(dados['email'], dados['username'], senha_hash)

    session['user_id'] = novo_usuario.id
    session['username'] = novo_usuario.username

    return jsonify({"success": True, "message": "Conta criada com sucesso!"}), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json()
    erro = validate_login_data(dados)
    if erro:
        return jsonify({"success": False, "message": erro}), 400

    usuario = repo.find_by_email(dados['email'])
    if not usuario or not verify_password(dados['password'], usuario.password_hash):
        return jsonify({"success": False, "message": "Dados incorretos."}), 401

    session['user_id'] = usuario.id
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
        return jsonify({"success": False}), 401
    return jsonify(repo_diario.listar(session['user_id'])), 200


@app.route('/api/diario', methods=['POST'])
def salvar_diario():
    if 'user_id' not in session:
        return jsonify({"success": False}), 401

    dados = request.get_json(silent=True) or {}
    texto = (dados.get('texto') or '').strip()

    if not texto:
        return jsonify({"success": False}), 400

    nova = repo_diario.criar(session['user_id'], texto)
    return jsonify({"success": True, "entrada": nova}), 201


@app.route('/api/diario/<int:entrada_id>', methods=['DELETE'])
def apagar_diario(entrada_id):
    if 'user_id' not in session:
        return jsonify({"success": False}), 401

    if not repo_diario.apagar(entrada_id, session['user_id']):
        return jsonify({"success": False}), 404

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
        banco_dados["contatos"].append({
            "nome": dados.get('nome'),
            "telefone": dados.get('telefone')
        })
        return jsonify({"success": True}), 200

    return jsonify({"success": False}), 400

@app.route('/api/ia/chat', methods=['POST'])
def chat_ia():
    dados = request.get_json()
    mensagem = dados.get("message", "")

    if not mensagem:
        return jsonify({"error": "Mensagem vazia"}), 400

    prompt = f"""
Você é uma maquiadora especialista.
Responda de forma simples, amigável e prática.

Usuário: {mensagem}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload)

    try:
        result = response.json()

        # formato do HF pode variar
        if isinstance(result, list):
            text = result[0].get("generated_text", "")
        else:
            text = result.get("generated_text", "")

        return jsonify({"response": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ia/tom-de-pele', methods=['POST'])
def api_tom_de_pele():
    dados = request.get_json()
    imagem_base64 = dados.get("image")

    if not imagem_base64:
        return jsonify({"error": "Sem imagem"}), 400

    # decode base64
    img_data = base64.b64decode(imagem_base64.split(",")[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # carregar detector de rosto
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    if len(faces) == 0:
        return jsonify({
            "error": "Nenhum rosto detectado"
        }), 400

    # pega o primeiro rosto
    (x, y, w, h) = faces[0]

    # região das bochechas (parte central do rosto)
    roi = img[
        y + int(h * 0.3): y + int(h * 0.7),
        x + int(w * 0.2): x + int(w * 0.8)
    ]

    # converte para YCrCb (melhor para pele)
    ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)

    cr = ycrcb[:, :, 1]
    cb = ycrcb[:, :, 2]

    mean_cr = float(np.mean(cr))
    mean_cb = float(np.mean(cb))

    # classificação mais realista (aproximação estética)
    if mean_cr > 150 and mean_cb < 120:
        tom = "Claro"
        subtom = "Quente"
    elif mean_cr > 140:
        tom = "Médio Claro"
        subtom = "Neutro Quente"
    elif mean_cr > 130:
        tom = "Médio"
        subtom = "Neutro"
    else:
        tom = "Escuro"
        subtom = "Frio / Neutro"

    return jsonify({
        "tom": tom,
        "subtom": subtom,
        "cr": mean_cr,
        "cb": mean_cb
    })


if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))