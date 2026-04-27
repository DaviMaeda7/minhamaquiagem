from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Banco de dados temporário para armazenar as informações durante a execução
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
    """Página inicial (Loja de Maquilhagem)."""
    return render_template('index.html')

@app.route('/login')
def login():
    """Página de acesso à área secreta."""
    return render_template('login.html')

@app.route('/home-secret')
def home_secret():
    """Painel principal da área segura."""
    return render_template('home_secret.html')

@app.route('/localizacao')
def pagina_localizacao():
    """Página com a funcionalidade de GPS."""
    return render_template('localizacao.html')

@app.route('/contanto')
def pagina_contatos():
    """Página de gestão de contactos de emergência."""
    return render_template('contanto.html')

@app.route('/diario')
def pagina_diario():
    """Página para escrever no diário secreto."""
    return render_template('diario.html')

# =============================================
# ROTAS DE API (PROCESSAMENTO DE DADOS)
# =============================================

@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json()
    # Exemplo de senha padrão
    if dados.get('senha') == 'segura123':
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "message": "Senha incorreta"}), 401

@app.route('/api/diario', methods=['POST'])
def salvar_diario():
    dados = request.get_json()
    texto = dados.get('texto')
    if texto:
        banco_dados["diario"].append(texto)
        print(f"Novo registro no diário: {texto}") # Aparece no seu terminal
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

# =============================================
# EXECUÇÃO DO PROJETO
# =============================================

if __name__ == '__main__':
    # O modo debug=True permite que o servidor reinicie sozinho ao salvar arquivos
    app.run(debug=True)