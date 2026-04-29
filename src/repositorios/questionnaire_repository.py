"""
questionnaire_repository.py
─────────────────────────────────────────────────────────────
Contrato para persistência de respostas do questionário.

Segue o mesmo padrão do UserRepository: qualquer banco futuro
implementa essa interface sem alterar mais nada.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QuestionnaireSubmission:
    """
    Representa uma submissão completa do questionário.

    answers é um dicionário: { id_da_pergunta (int) -> resposta (str) }
    Exemplo: { 1: "A", 2: "C", 3: "B" }

    As respostas chegam aqui já validadas e saem daqui criptografadas
    para o banco — esse dataclass trafega dados limpos entre camadas.
    """
    user_id:    int
    answers:    dict[int, str]
    id:         int | None          = None
    submitted_at: datetime | None   = None


class QuestionnaireRepository(ABC):

    @abstractmethod
    def save(self, submission: QuestionnaireSubmission) -> QuestionnaireSubmission:
        """
        Persiste as respostas criptografadas.
        Retorna o objeto com id e submitted_at preenchidos.
        """
        ...

    @abstractmethod
    def find_by_user(self, user_id: int) -> list[QuestionnaireSubmission]:
        """
        Retorna todas as submissões de um usuário (descriptografadas).
        Usado futuramente pelo módulo de cálculo de perigo.
        """
        ...

    @abstractmethod
    def find_latest_by_user(self, user_id: int) -> QuestionnaireSubmission | None:
        """
        Retorna somente a submissão mais recente do usuário.
        É o que o módulo de cálculo de perigo usará na prática.
        """
        ...
