"""
app.py
─────────────────────────────────────────────────────────────
Ponto de entrada unificado do servidor 'Minha Maquiagem'.
Serve as telas frontend (HTML) e registra a API de backend.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente (senhas, chaves do banco) ANTES de tudo
load_dotenv()

from flask import Flask, render_template

# ── Imports da Nova Arquitetura (Backend) ──
# Note que agora o Python busca dentro da pasta 'src'
from src.rotas.auth_routes import auth_bp
from src.rotas.questionnaire_routes import questionnaire_bp

app = Flask(__name__)

# ── Registro da API Backend (Blueprints) ──
# Usamos url_prefix='/api' para que a lógica não colida com as telas HTML
# Ex: O login visual é '/login', mas o envio dos dados é para '/api/auth/login'
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(questionnaire_bp, url_prefix='/api')


# ── Rotas Frontend (Telas Visuais) ──
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home-secret')
def homesecret():
    return render_template('home_secret.html')


# ── Execução do Servidor ──
if __name__ == '__main__':
    # Validação rápida de segurança ao ligar o servidor
    if not os.getenv("QUESTIONNAIRE_SECRET_KEY"):
        print("⚠️ AVISO: QUESTIONNAIRE_SECRET_KEY não encontrada no .env!")
        print("A criptografia do banco poderá falhar.")
        
    print("🚀 Servidor 'Minha Maquiagem' iniciando na porta 5000...")
    app.run(debug=True, port=5000)