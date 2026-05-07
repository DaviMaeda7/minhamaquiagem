from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'meu_escudo_secreto_2024'  # necessário para session

banco_dados = {
    "diario": [],
    "contatos_emergencia": [
        {"nome": "Polícia Militar — DF",         "telefone": "190"},
        {"nome": "Central de Atendimento à Mulher", "telefone": "180"},
        {"nome": "SAMU",                          "telefone": "192"},
        {"nome": "DEAM — Delegacia da Mulher DF", "telefone": "6132425813"},
        {"nome": "Casa da Mulher Brasileira — DF","telefone": "6132040033"},
    ],
    "voluntarias": [
        {
            "id": 1,
            "emoji": "👩‍⚖️",
            "nome": "Dra. Carla Mendes",
            "area": "Advogada",
            "desc": "Orientação jurídica gratuita em casos de violência doméstica. Medidas protetivas e BO.",
            "tags": ["Jurídico", "Medida Protetiva", "BO"],
            "telefone": "61999990001",
            "whatsapp": "5561999990001",
            "status": "ativa"
        },
        {
            "id": 2,
            "emoji": "🧠",
            "nome": "Psic. Renata Oliveira",
            "area": "Psicóloga",
            "desc": "Suporte emocional especializado para vítimas de violência. Atendimento online disponível.",
            "tags": ["Psicológico", "Online", "Trauma"],
            "telefone": "61999990002",
            "whatsapp": "5561999990002",
            "status": "ativa"
        },
        {
            "id": 3,
            "emoji": "🤝",
            "nome": "Ana Paula Santos",
            "area": "Assistente Social",
            "desc": "Auxílio com documentação, abrigos e encaminhamentos para serviços sociais do DF.",
            "tags": ["Social", "Abrigos", "Documentos"],
            "telefone": "61999990003",
            "whatsapp": "5561999990003",
            "status": "ativa"
        },
        {
            "id": 4,
            "emoji": "⚕️",
            "nome": "Dra. Fernanda Lima",
            "area": "Médica",
            "desc": "Orientação sobre laudos médicos para processos judiciais e atendimento de saúde prioritário.",
            "tags": ["Saúde", "Laudos", "Médica"],
            "telefone": "61999990004",
            "whatsapp": "5561999990004",
            "status": "ativa"
        },
    ],
    "candidatas_voluntarias": [],  # cadastros pendentes de aprovação
    "questionarios": [],
    "alertas_sos": [],             # registro de acionamentos SOS
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


# =============================================
# API — AUTENTICAÇÃO
# =============================================

@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json()
    if not dados:
        return jsonify({"success": False, "message": "Dados inválidos"}), 400

    if dados.get('senha') == 'segura123':
        session['autenticada'] = True
        return jsonify({"success": True}), 200

    return jsonify({"success": False, "message": "Senha incorreta"}), 401


# =============================================
# API — DIÁRIO
# =============================================

@app.route('/api/diario', methods=['GET'])
def listar_diario():
    return jsonify(banco_dados["diario"]), 200

@app.route('/api/diario', methods=['POST'])
def salvar_diario():
    dados = request.get_json()
    texto = dados.get('texto') if dados else None
    if texto:
        entrada = {
            "id": len(banco_dados["diario"]) + 1,
            "texto": texto,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        banco_dados["diario"].insert(0, entrada)
        print(f"[DIÁRIO] Nova entrada: {texto[:60]}...")
        return jsonify({"success": True, "entrada": entrada}), 200
    return jsonify({"success": False, "message": "Texto vazio"}), 400

@app.route('/api/diario/<int:entrada_id>', methods=['DELETE'])
def apagar_diario(entrada_id):
    original = len(banco_dados["diario"])
    banco_dados["diario"] = [e for e in banco_dados["diario"] if e["id"] != entrada_id]
    if len(banco_dados["diario"]) < original:
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "message": "Entrada não encontrada"}), 404


# =============================================
# API — QUESTIONÁRIO
# =============================================

@app.route('/api/questionario', methods=['POST'])
def salvar_questionario():
    dados = request.get_json()
    respostas = dados.get('respostas') if dados else None
    nivel     = dados.get('nivel')
    if respostas:
        registro = {
            "id": len(banco_dados["questionarios"]) + 1,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "respostas": respostas,
            "nivel_risco": nivel
        }
        banco_dados["questionarios"].append(registro)
        print(f"[QUESTIONÁRIO] Respondido — nível de risco: {nivel}")
        return jsonify({"success": True, "nivel": nivel}), 200
    return jsonify({"success": False, "message": "Sem respostas"}), 400


# =============================================
# API — CONTATOS DE EMERGÊNCIA
# =============================================

@app.route('/api/contatos', methods=['GET'])
def listar_contatos():
    return jsonify(banco_dados["contatos_emergencia"]), 200

@app.route('/api/contatos', methods=['POST'])
def adicionar_contato():
    dados = request.get_json()
    nome     = dados.get('nome')     if dados else None
    telefone = dados.get('telefone') if dados else None
    if nome and telefone:
        banco_dados["contatos_emergencia"].append({
            "nome": nome,
            "telefone": telefone
        })
        print(f"[CONTATO] Adicionado: {nome} — {telefone}")
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "message": "Nome e telefone obrigatórios"}), 400


# =============================================
# API — VOLUNTÁRIAS
# =============================================

@app.route('/api/voluntarias', methods=['GET'])
def listar_voluntarias():
    """Retorna voluntárias ativas. Aceita ?busca=termo para filtrar."""
    busca = request.args.get('busca', '').lower()
    resultado = [
        v for v in banco_dados["voluntarias"]
        if v["status"] == "ativa" and (
            not busca or
            busca in v["nome"].lower() or
            busca in v["area"].lower() or
            any(busca in tag.lower() for tag in v["tags"])
        )
    ]
    return jsonify(resultado), 200

@app.route('/api/voluntarias/candidatura', methods=['POST'])
def cadastrar_candidata_voluntaria():
    """Recebe candidatura de nova voluntária (fica pendente de aprovação)."""
    dados = request.get_json()
    nome  = dados.get('nome')  if dados else None
    area  = dados.get('area')  if dados else None
    tel   = dados.get('telefone') if dados else None
    desc  = dados.get('descricao', '') if dados else ''

    if nome and area and tel:
        candidatura = {
            "id":        len(banco_dados["candidatas_voluntarias"]) + 1,
            "nome":      nome,
            "area":      area,
            "telefone":  tel,
            "descricao": desc,
            "data":      datetime.now().strftime("%d/%m/%Y %H:%M"),
            "status":    "pendente"
        }
        banco_dados["candidatas_voluntarias"].append(candidatura)
        print(f"[VOLUNTÁRIA] Nova candidatura: {nome} — {area}")
        return jsonify({"success": True, "message": "Candidatura recebida! Nossa equipe entrará em contato."}), 200

    return jsonify({"success": False, "message": "Nome, área e telefone são obrigatórios"}), 400

@app.route('/api/voluntarias/candidaturas', methods=['GET'])
def listar_candidaturas():
    """Lista candidaturas pendentes (uso interno/admin)."""
    return jsonify(banco_dados["candidatas_voluntarias"]), 200


# =============================================
# API — SOS / ALERTA DE EMERGÊNCIA
# =============================================

@app.route('/api/sos', methods=['POST'])
def registrar_sos():
    """Registra um acionamento SOS com localização e timestamp."""
    dados = request.get_json()
    lat   = dados.get('latitude')   if dados else None
    lng   = dados.get('longitude')  if dados else None

    alerta = {
        "id":        len(banco_dados["alertas_sos"]) + 1,
        "data":      datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "latitude":  lat,
        "longitude": lng,
        "maps_link": f"https://maps.google.com/?q={lat},{lng}" if lat and lng else None,
        "status":    "disparado"
    }
    banco_dados["alertas_sos"].append(alerta)
    print(f"[🚨 SOS] Alerta #{alerta['id']} registrado em {alerta['data']} | Localização: {lat}, {lng}")

    return jsonify({
        "success":   True,
        "alerta_id": alerta["id"],
        "maps_link": alerta["maps_link"],
        "message":   "Alerta registrado. Contatos notificados."
    }), 200

@app.route('/api/sos/historico', methods=['GET'])
def historico_sos():
    """Retorna histórico de alertas SOS (uso interno)."""
    return jsonify(banco_dados["alertas_sos"]), 200


# =============================================
# EXECUÇÃO DO PROJETO
# =============================================

if __name__ == '__main__':
    app.run(debug=True)