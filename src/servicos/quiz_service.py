# src/servicos/quiz_service.py

def calcular_resultado_quiz(respostas_indices):
    """
    Recebe uma lista com os índices (0, 1, 2, 3) das opções selecionadas
    nas 6 perguntas e retorna os níveis de risco e o perfil predominante.
    """
    
    # Estrutura de pontuações espelhada do código original (TypeScript)
    pontuacoes_perguntas = [
        # Pergunta 1
        [
            {"fisica": 0, "emocional": 0, "patrimonial": 0}, # 0: Nunca
            {"fisica": 1, "emocional": 1, "patrimonial": 0}, # 1: Raramente
            {"fisica": 2, "emocional": 2, "patrimonial": 1}, # 2: Às vezes
            {"fisica": 3, "emocional": 3, "patrimonial": 1}  # 3: Frequentemente
        ],
        # Pergunta 2
        [
            {"fisica": 0, "emocional": 0, "patrimonial": 0}, # 0: Não
            {"fisica": 0, "emocional": 1, "patrimonial": 2}, # 1: Um pouco
            {"fisica": 1, "emocional": 2, "patrimonial": 3}, # 2: Sim, bastante
            {"fisica": 1, "emocional": 3, "patrimonial": 4}  # 3: Controle total
        ],
        # Pergunta 3
        [
            {"fisica": 0, "emocional": 0, "patrimonial": 0}, # 0: Nunca
            {"fisica": 0, "emocional": 2, "patrimonial": 0}, # 1: Poucas vezes
            {"fisica": 1, "emocional": 3, "patrimonial": 1}, # 2: Com frequência
            {"fisica": 2, "emocional": 4, "patrimonial": 1}  # 3: Totalmente isolada
        ],
        # Pergunta 4
        [
            {"fisica": 0, "emocional": 0, "patrimonial": 0}, # 0: Nunca
            {"fisica": 1, "emocional": 2, "patrimonial": 0}, # 1: Verbais leves
            {"fisica": 2, "emocional": 3, "patrimonial": 0}, # 2: Verbais graves
            {"fisica": 4, "emocional": 3, "patrimonial": 0}  # 3: Físicas
        ],
        # Pergunta 5
        [
            {"fisica": 0, "emocional": 0, "patrimonial": 0}, # 0: Sim, todos comigo
            {"fisica": 0, "emocional": 1, "patrimonial": 2}, # 1: Alguns com outra pessoa
            {"fisica": 1, "emocional": 2, "patrimonial": 4}  # 2: Não tenho acesso
        ],
        # Pergunta 6
        [
            {"fisica": 0, "emocional": 0, "patrimonial": 0}, # 0: Não
            {"fisica": 1, "emocional": 2, "patrimonial": 0}, # 1: Às vezes
            {"fisica": 2, "emocional": 4, "patrimonial": 1}  # 2: Sim, sempre
        ]
    ]

    # Dados dos perfis vencedores (Textos e Recomendações)
    perfis = {
        "fisica": {
            "nome": "Risco de Violência Física",
            "descricao": "Os sinais indicam possível exposição a violência física. Sua segurança é prioridade.",
            "recomendacoes": [
                "Ligue 180 ou 190 imediatamente se estiver em perigo",
                "Prepare um plano de fuga com documentos e pertences essenciais",
                "Registre boletim de ocorrência na delegacia mais próxima",
                "Procure um abrigo ou casa de acolhimento",
            ]
        },
        "emocional": {
            "nome": "Risco de Violência Psicológica",
            "descricao": "Há indicadores de controle emocional e manipulação. Você merece relações saudáveis.",
            "recomendacoes": [
                "Busque acompanhamento psicológico — CAPS e UBS oferecem gratuitamente",
                "Converse com alguém de confiança sobre sua situação",
                "Documente episódios de abuso emocional",
                "A Lei Maria da Penha protege contra violência psicológica",
            ]
        },
        "patrimonial": {
            "nome": "Risco de Violência Patrimonial",
            "descricao": "Os sinais apontam controle financeiro e patrimonial. Você tem direitos garantidos por lei.",
            "recomendacoes": [
                "Guarde cópias de documentos pessoais em local seguro",
                "Procure a Defensoria Pública para orientação jurídica gratuita",
                "Abra uma conta bancária individual se possível",
                "Violência patrimonial é crime previsto na Lei Maria da Penha",
            ]
        }
    }

    # 1. Somar os pontos com base nas respostas dadas
    pontuacao_total = {"fisica": 0, "emocional": 0, "patrimonial": 0}
    
    for indice_pergunta, resposta_dada in enumerate(respostas_indices):
        pontos_da_resposta = pontuacoes_perguntas[indice_pergunta][resposta_dada]
        pontuacao_total["fisica"] += pontos_da_resposta["fisica"]
        pontuacao_total["emocional"] += pontos_da_resposta["emocional"]
        pontuacao_total["patrimonial"] += pontos_da_resposta["patrimonial"]

    # 2. Descobrir qual é o perfil com a maior pontuação
    # Em caso de empate, ele pegará a primeira chave definida
    chave_vencedora = max(pontuacao_total, key=pontuacao_total.get)
    perfil_vencedor = perfis[chave_vencedora]

    # 3. Calcular o nível de risco de cada categoria (Baixo, Moderado, Alto)
    niveis_risco = {}
    for categoria, score in pontuacao_total.items():
        if score <= 3:
            niveis_risco[categoria] = {"label": "Baixo", "cor": "verde"}
        elif score <= 7:
            niveis_risco[categoria] = {"label": "Moderado", "cor": "amarelo"}
        else:
            niveis_risco[categoria] = {"label": "Alto", "cor": "vermelho"}

    # 4. Retornar os dados consolidados para o Flask/HTML
    return {
        "pontuacoes": pontuacao_total,
        "niveis_risco": niveis_risco,
        "perfil_predominante": perfil_vencedor
    }