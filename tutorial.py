"""
GUIA DE IMPLEMENTAÇÃO DO QUIZ NO HTML (Para a equipe de Frontend)

1. ARQUIVO: templates/quiz.html
---------------------------------------------------------
O formulário de perguntas deve enviar os dados via POST para a rota /submit-quiz.
Os "names" dos inputs de rádio devem ser q1, q2, q3, q4, q5 e q6.
Os "values" devem ser de 0 a 3 (ou 0 a 2 dependendo da pergunta).

Exemplo de estrutura:
<form action="/submit-quiz" method="POST">
    <h3>Com que frequência você se sente insegura em casa?</h3>
    <input type="radio" name="q1" value="0" required> Nunca
    <input type="radio" name="q1" value="1"> Raramente
    <input type="radio" name="q1" value="2"> Às vezes
    <input type="radio" name="q1" value="3"> Frequentemente
    
    <button type="submit">Ver Resultado</button>
</form>

2. ARQUIVO: templates/resultado_quiz.html
---------------------------------------------------------
O Backend vai devolver um objeto Jinja chamado `resultado`.
Você pode usar as variáveis abaixo para exibir na tela:

<h1>Resultado do seu Quiz</h1>
<h2>Perfil Predominante: {{ resultado.perfil_predominante.nome }}</h2>
<p>{{ resultado.perfil_predominante.descricao }}</p>

<h3>O que fazer:</h3>
<ul>
    {% for rec in resultado.perfil_predominante.recomendacoes %}
        <li>{{ rec }}</li>
    {% endfor %}
</ul>

<h3>Resumo dos Níveis:</h3>
<p>Risco Físico: {{ resultado.niveis_risco.fisica.label }}</p>
<p>Risco Emocional: {{ resultado.niveis_risco.emocional.label }}</p>
<p>Risco Patrimonial: {{ resultado.niveis_risco.patrimonial.label }}</p>
"""