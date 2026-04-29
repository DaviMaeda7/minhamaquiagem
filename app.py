import os
from dotenv import load_dotenv

# Carrega as configurações de segurança (.env)
load_dotenv()

from flask import Flask, render_template

# ── Imports da Arquitetura de Backend ──
from src.rotas.auth_routes import auth_bp
from src.rotas.questionnaire_routes import questionnaire_bp

app = Flask(__name__)

# Registo da API (Lógica de Login e Questionário)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(questionnaire_bp, url_prefix='/api')


# ── Rotas das Telas (Frontend) ──

@app.route('/')
def login_page():
    """Agora a página de entrada oficial do sistema é o Login."""
    return render_template('login.html')

@app.route('/vitrine')
def index():
    """A vitrine de maquiagem (o disfarce) continua disponível aqui."""
    return render_template('index.html')

@app.route('/home-secret')
def homesecret():
    """A área secreta após o login."""
    return render_template('home_secret.html')


# ── Inicialização Segura ──
if __name__ == '__main__':
    # Garante que o banco de dados é criado antes de o site abrir
    from src.repositorios.sqlite_repository import init_db
    from src.repositorios.sqlite_questionnaire_repository import init_questionnaire_table
    
    init_db()
    init_questionnaire_table()
    
    print("✅ Servidor pronto: O Login é agora a página inicial.")
    app.run(debug=True, port=5000)
