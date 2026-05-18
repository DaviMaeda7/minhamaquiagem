"""
auth_routes.py
─────────────────────────────────────────────────────────────
Módulo independente para Cadastro e Login.
"""
from flask import Blueprint, request, jsonify
from src.factory import get_user_repository
from src.servicos.auth import hash_password, validate_signup_data, validate_login_data, verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corpo da requisição inválido."}), 400

    error = validate_signup_data(data)
    if error:
        return jsonify({"error": error}), 422

    email = data["email"].strip().lower()
    username = data["username"].strip()
    password = data["password"]

    repo = get_user_repository()
    taken = repo.exists(email, username)

    if taken["email"]:
        return jsonify({"error": "E-mail já cadastrado."}), 409
    if taken["username"]:
        return jsonify({"error": "Nome de usuário em uso."}), 409

    hashed = hash_password(password)
    user = repo.create(email, username, hashed)

    return jsonify({
        "message": "Usuário cadastrado com sucesso!",
        "user_id": user.id
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Corpo da requisição inválido."}), 400

    error = validate_login_data(data)
    if error:
        return jsonify({"error": error}), 422

    email = data["email"].strip().lower()
    password = data["password"]

    repo = get_user_repository()
    user = repo.find_by_email(email)

    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "E-mail ou senha inválidos."}), 401

    return jsonify({
        "message": "Login realizado com sucesso!",
        "user_id": user.id
    }), 200