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
        {"nome": "Polícia",                        "telefone": "190"},
        {"nome": "Central de Atendimento à Mulher","telefone": "180"},
        {"nome": "SAMU",                           "telefone": "192"}
    ],
    "questionarios": []
}

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"

hf_headers = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}"
}

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ── Páginas públicas ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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

# ── Inspirações ───────────────────────────────────────────────────────────────
# FIX: rotas alinhadas com os slugs usados no quiz
# (beginner / natural / soft / glam / creative)

@app.route('/inspiracoes')
def inspiracoes():
    return render_template('inspiracoes.html')

@app.route('/inspiracoes/beginner')
def inspiracoes_beginner():
    return render_template('easy.html')

@app.route('/inspiracoes/natural')
def inspiracoes_natural():
    return render_template('natural.html')

@app.route('/inspiracoes/soft')
def inspiracoes_soft():
    return render_template('soft.html')

@app.route('/inspiracoes/glam')
def inspiracoes_glam():
    return render_template('full.html')

@app.route('/inspiracoes/creative')
def inspiracoes_creative():
    return render_template('criativa.html')

# ── Páginas protegidas ────────────────────────────────────────────────────────

@app.route('/home-secret')
def homesecret():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('home_secret.html')

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

# ── Auth ──────────────────────────────────────────────────────────────────────

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

    senha_hash   = hash_password(dados['password'])
    novo_usuario = repo.create(dados['email'], dados['username'], senha_hash)

    session['user_id']  = novo_usuario.id
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

    session['user_id']  = usuario.id
    session['username'] = usuario.username

    return jsonify({"success": True}), 200


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True}), 200

# ── Diário ────────────────────────────────────────────────────────────────────

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

# ── Questionário ──────────────────────────────────────────────────────────────

@app.route('/api/questionario', methods=['POST'])
def salvar_questionario():
    dados = request.get_json()

    if dados.get('respostas'):
        banco_dados["questionarios"].append({
            "data":              datetime.now().strftime("%d/%m/%Y %H:%M"),
            "respostas":         dados.get('respostas'),
            "nivel_risco_front": dados.get('nivel')
        })
        return jsonify({"success": True}), 200

    return jsonify({"success": False}), 400

# ── Contatos ──────────────────────────────────────────────────────────────────

@app.route('/api/contatos', methods=['GET'])
def listar_contatos():
    return jsonify(banco_dados["contatos"]), 200


@app.route('/api/contatos', methods=['POST'])
def adicionar_contato():
    dados = request.get_json()

    if dados.get('nome') and dados.get('telefone'):
        banco_dados["contatos"].append({
            "nome":     dados.get('nome'),
            "telefone": dados.get('telefone')
        })
        return jsonify({"success": True}), 200

    return jsonify({"success": False}), 400

# ── IA: Chat ──────────────────────────────────────────────────────────────────

@app.route('/api/ia/chat', methods=['POST'])
def chat_ia():
    dados = request.get_json()
    mensagem = dados.get("message", "").strip()

    if not mensagem:
        return jsonify({"error": "Mensagem vazia"}), 400

    if not os.getenv("HF_API_KEY"):
        return jsonify({"error": "HF_API_KEY não configurada"}), 500

    prompt = f"""Você é uma maquiadora especialista.
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

    try:
        response = requests.post(
            HF_API_URL,
            headers=hf_headers,
            json=payload,
            timeout=20
        )

        result = response.json()

        if response.status_code != 200:
            return jsonify({"response": "Erro na IA (HF indisponível no momento)."})

        if isinstance(result, dict) and "error" in result:
            return jsonify({"response": "Modelo ainda carregando. Tente novamente em alguns segundos."})

        if isinstance(result, list) and "generated_text" in result[0]:
            full = result[0]["generated_text"]
            text = full.split("Usuário:")[-1].strip() if "Usuário:" in full else full
        else:
            text = "Não consegui gerar resposta no momento."

        return jsonify({"response": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── IA: Tom de pele ───────────────────────────────────────────────────────────
# FIX: renomeada de tom_de_pele → api_tom_de_pele para evitar conflito de endpoint

@app.route('/api/ia/tom-de-pele', methods=['POST'])
def api_tom_de_pele():
    dados = request.get_json()
    imagem_base64 = dados.get("image")

    if not imagem_base64:
        return jsonify({"error": "Sem imagem"}), 400

    try:
        img_data = base64.b64decode(imagem_base64.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Imagem inválida"}), 400

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        if len(faces) == 0:
            return jsonify({"error": "Nenhum rosto detectado (tente iluminação melhor)"}), 400

        x, y, w, h = faces[0]

        h_img, w_img = img.shape[:2]

        x1 = max(0, x + int(w * 0.2))
        x2 = min(w_img, x + int(w * 0.8))
        y1 = max(0, y + int(h * 0.3))
        y2 = min(h_img, y + int(h * 0.7))

        if x2 <= x1 or y2 <= y1:
            return jsonify({"error": "Região inválida"}), 400

        roi = img[y1:y2, x1:x2]

        if roi.size == 0:
            return jsonify({"error": "Falha ao extrair pele"}), 400

        ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)

        mean_cr = float(np.mean(ycrcb[:, :, 1]))
        mean_cb = float(np.mean(ycrcb[:, :, 2]))

        if mean_cr > 150 and mean_cb < 120:
            tom, subtom = "Claro", "Quente"
        elif mean_cr > 140:
            tom, subtom = "Médio Claro", "Neutro Quente"
        elif mean_cr > 130:
            tom, subtom = "Médio", "Neutro"
        else:
            tom, subtom = "Escuro", "Frio / Neutro"

        return jsonify({
            "tom": tom,
            "subtom": subtom,
            "cr": mean_cr,
            "cb": mean_cb
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))