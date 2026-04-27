"""
auth.py
Regras de validação e segurança de senhas.
"""
import bcrypt
import re

def hash_password(password: str) -> bytes:
    # Transforma a senha "1234" em um código irreversível
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def validate_signup_data(data: dict) -> str | None:
    if not data.get("email") or not data.get("username") or not data.get("password"):
        return "Preencha todos os campos obrigatórios."
    if data["password"] != data.get("confirm_password"):
        return "As senhas não coincidem."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        return "Formato de e-mail inválido."
    return None

def validate_login_data(data: dict) -> str | None:
    if not data.get("email") or not data.get("password"):
        return "Preencha e-mail e senha."
    return None