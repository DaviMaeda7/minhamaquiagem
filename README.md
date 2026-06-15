# Minha Maquiagem - Painel de Análise de Segurança Pública

Este projeto consiste em um dashboard interativo focado na análise de dados de segurança pública, com ênfase na série histórica de feminicídios por Regiões Administrativas (RAs). O sistema realiza o mapeamento de ocorrências, taxas por 100 mil habitantes e cruzamento de dados estatísticos para apoio à tomada de decisão e conscientização.

---

## 🗂️ Estrutura da Pasta `templates/`

A pasta `templates/` gerencia o ecossistema de visualização da interface do usuário (Frontend). Abaixo está a descrição técnica do papel de cada arquivo no fluxo do sistema:

### Autenticação e Controle de Acesso
* **`cadastro.html`**: Interface para registro de novos usuários e administradores do painel.
* **`home-visitor.html`**: Tela inicial voltada para o público geral, com visualizações simplificadas e informativas.
* **`home_secret.html`**: Painel administrativo restrito para inserção, edição ou auditoria de dados estatísticos sensíveis.

### Painéis de Dados e Funcionalidades Core
* **`index.html`**: A página principal do ecossistema. Renderiza a série histórica completa, os cards de métricas acumuladas e os gráficos consolidados.
* **`dados.html`**: Tela dedicada a relatórios tabulares, filtros avançados de exportação de dados brutos e planilhas.
* **`diario.html`**: Feed cronológico de atualizações de ocorrências, boletins informativos ou logs de auditoria do sistema.
* **`contatos.html`**: Central de suporte, canais diretos de ouvidoria e catálogo de redes de apoio técnico ou social.
* **`chat-box.html`**: Componente de interface de mensageria integrada para suporte técnico interno ou atendimento ao usuário.

### Interfaces Adaptativas de Layout
* **`criativa.html` / `easy.html` / `full.html` / `inspiracoes.html`**: Módulos de interface adaptados para diferentes resoluções ou perfis de visualização (visões simplificadas para dispositivos móveis, dashboards em tela cheia para salas de controle ou protótipos de inspiração visual).

---

## 🗺️ Arquitetura de Rotas (Backend)

O backend do projeto (implementado utilizando frameworks Python como **Flask** ou **FastAPI**) mapeia as requisições HTTP para entregar os respectivos templates da aplicação.

| Rota HTTP | Método | Template Renderizado | Objetivo Técnico |
| :--- | :--- | :--- | :--- |
| `/` , `/index` | `GET` | `index.html` | Exibição da Série Histórica (Painel Geral) |
| `/cadastro` | `GET/POST`| `cadastro.html` | Criação de novas credenciais no sistema |
| `/dados` | `GET` | `dados.html` | Visualização detalhada de dados e Mapas por RA |
| `/diario` | `GET` | `diario.html` | Visualização de logs de ocorrência e bairros de risco |
| `/api/estatisticas`| `GET` | *(Retorna JSON)* | Endpoint de API que alimenta os gráficos dinamicamente |

### Exemplo de Implementação de Rota (Python/Flask)
```python
@app.route('/index')
def index():
    # Renderiza o painel principal com os componentes visuais
    return render_template('index.html')
